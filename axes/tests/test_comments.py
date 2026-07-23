from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from axes.models import Comment, Settings
from axes.services.comments import build_comment_tree
from axes.tests.factories import make_axe, make_manufacturer, make_stamp


class CommentModelTest(TestCase):
    def test_clean_requires_exactly_one_target(self):
        axe = make_axe()
        manufacturer = make_manufacturer()

        with self.assertRaises(ValidationError):
            Comment(body="Test").full_clean()

        with self.assertRaises(ValidationError):
            Comment(axe=axe, manufacturer=manufacturer, body="Test").full_clean()

        # Exakt en satt (axe) ska passera clean() utan att höja ValidationError
        Comment(axe=axe, body="Test").full_clean()

    def test_clean_rejects_self_reference(self):
        axe = make_axe()
        comment = Comment.objects.create(axe=axe, body="Test", status="APPROVED")
        comment.parent = comment
        with self.assertRaises(ValidationError):
            comment.full_clean()

    def test_clean_rejects_parent_with_different_target(self):
        axe = make_axe()
        other_axe = make_axe()
        parent = Comment.objects.create(axe=axe, body="Förälder", status="APPROVED")
        child = Comment(axe=other_axe, parent=parent, body="Svar")
        with self.assertRaises(ValidationError):
            child.full_clean()

    def test_depth_is_clamped_to_max_depth(self):
        axe = make_axe()
        comment = None
        for i in range(Comment.MAX_DEPTH + 3):
            comment = Comment.objects.create(
                axe=axe, parent=comment, body=f"Nivå {i}", status="APPROVED"
            )
        self.assertEqual(comment.depth, Comment.MAX_DEPTH)

    def test_line_class_for_depth_0_to_5(self):
        axe = make_axe()
        expected = {0: "lvl1", 1: "lvl2", 2: "lvl3", 3: "lvl4", 4: "lvl5", 5: "lvl1"}
        for depth, expected_class in expected.items():
            comment = Comment(axe=axe, body="Test", depth=depth)
            self.assertEqual(comment.line_class, expected_class)


class BuildCommentTreeTest(TestCase):
    def test_only_approved_comments_are_included_for_anonymous(self):
        axe = make_axe()
        Comment.objects.create(axe=axe, body="Godkänd", status="APPROVED")
        Comment.objects.create(axe=axe, body="Väntar", status="PENDING")
        Comment.objects.create(axe=axe, body="Avvisad", status="REJECTED")

        tree = build_comment_tree(axe, is_staff=False)

        self.assertEqual(len(tree), 1)
        self.assertEqual(tree[0].body, "Godkänd")

    def test_top_level_is_newest_first(self):
        axe = make_axe()
        first = Comment.objects.create(axe=axe, body="Först", status="APPROVED")
        second = Comment.objects.create(axe=axe, body="Sedan", status="APPROVED")

        tree = build_comment_tree(axe, is_staff=False)

        self.assertEqual([c.pk for c in tree], [second.pk, first.pk])

    def test_root_nodes_have_no_rendered_children_when_no_replies(self):
        axe = make_axe()
        Comment.objects.create(axe=axe, body="Ensam", status="APPROVED")

        tree = build_comment_tree(axe, is_staff=False)

        self.assertEqual(tree[0].rendered_children, [])

    def test_one_level_reply_is_nested_under_parent(self):
        axe = make_axe()
        root = Comment.objects.create(axe=axe, body="Rot", status="APPROVED")
        reply = Comment.objects.create(
            axe=axe, parent=root, body="Svar", status="APPROVED"
        )

        tree = build_comment_tree(axe, is_staff=False)

        self.assertEqual(len(tree[0].rendered_children), 1)
        self.assertEqual(tree[0].rendered_children[0].pk, reply.pk)
        self.assertEqual(tree[0].rendered_children[0].rendered_children, [])

    def test_replies_deeper_than_max_depth_are_hoisted_as_siblings(self):
        axe = make_axe()
        comment = None
        chain = []
        for i in range(Comment.MAX_DEPTH + 3):  # två nivåer djupare än taket
            comment = Comment.objects.create(
                axe=axe, parent=comment, body=f"Nivå {i}", status="APPROVED"
            )
            chain.append(comment)

        tree = build_comment_tree(axe, is_staff=False)

        # Gå ner till noden som ligger exakt på MAX_DEPTH - varje nivå på
        # vägen dit ska ha exakt ett barn (rak kedja).
        node = tree[0]
        for _ in range(Comment.MAX_DEPTH):
            self.assertEqual(len(node.rendered_children), 1)
            node = node.rendered_children[0]

        # node är nu kedjans MAX_DEPTH:e länk - alla djupare svar ska ligga
        # hissade som strukturella syskon här, kronologiskt, utan egna barn.
        hoisted = chain[Comment.MAX_DEPTH + 1 :]
        self.assertEqual(
            [c.pk for c in node.rendered_children], [c.pk for c in hoisted]
        )
        for hoisted_node in node.rendered_children:
            self.assertEqual(hoisted_node.rendered_children, [])

    def test_approved_reply_under_rejected_parent_is_stub_for_anonymous(self):
        axe = make_axe()
        parent = Comment.objects.create(axe=axe, body="Avvisad", status="REJECTED")
        reply = Comment.objects.create(
            axe=axe, parent=parent, body="Godkänt svar", status="APPROVED"
        )

        tree = build_comment_tree(axe, is_staff=False)

        self.assertEqual(len(tree), 1)
        stub = tree[0]
        self.assertEqual(stub.pk, parent.pk)
        self.assertTrue(stub.is_visible_stub)
        self.assertEqual(stub.stub_reason, "moderated")
        self.assertEqual(len(stub.rendered_children), 1)
        self.assertEqual(stub.rendered_children[0].pk, reply.pk)
        self.assertFalse(stub.rendered_children[0].is_visible_stub)

    def test_rejected_leaf_comment_is_pruned_away(self):
        axe = make_axe()
        Comment.objects.create(axe=axe, body="Godkänd", status="APPROVED")
        Comment.objects.create(axe=axe, body="Avvisad lövnod", status="REJECTED")

        tree = build_comment_tree(axe, is_staff=False)

        self.assertEqual(len(tree), 1)
        self.assertEqual(tree[0].body, "Godkänd")

    def test_pending_with_approved_child_is_stub_for_anonymous_but_full_for_staff(
        self,
    ):
        axe = make_axe()
        parent = Comment.objects.create(axe=axe, body="Väntar", status="PENDING")
        Comment.objects.create(
            axe=axe, parent=parent, body="Godkänt svar", status="APPROVED"
        )

        anon_tree = build_comment_tree(axe, is_staff=False)
        self.assertEqual(len(anon_tree), 1)
        self.assertTrue(anon_tree[0].is_visible_stub)
        self.assertEqual(anon_tree[0].stub_reason, "pending")

        staff_tree = build_comment_tree(axe, is_staff=True)
        self.assertEqual(len(staff_tree), 1)
        self.assertFalse(staff_tree[0].is_visible_stub)
        self.assertEqual(staff_tree[0].body, "Väntar")

    def test_pending_leaf_comment_is_pruned_for_anonymous(self):
        axe = make_axe()
        Comment.objects.create(axe=axe, body="Väntar", status="PENDING")

        tree = build_comment_tree(axe, is_staff=False)

        self.assertEqual(tree, [])

    def test_removed_comment_with_reply_is_stub_with_removed_reason(self):
        axe = make_axe()
        parent = Comment.objects.create(
            axe=axe, body="Borttagen", status="APPROVED", is_removed=True
        )
        reply = Comment.objects.create(
            axe=axe, parent=parent, body="Svar kvar", status="APPROVED"
        )

        tree = build_comment_tree(axe, is_staff=False)

        self.assertEqual(len(tree), 1)
        self.assertTrue(tree[0].is_visible_stub)
        self.assertEqual(tree[0].stub_reason, "removed")
        self.assertEqual(tree[0].rendered_children[0].pk, reply.pk)

    def test_hoisting_and_pruning_combine_correctly(self):
        # Kedja MAX_DEPTH+3 djup, med den sista länken REJECTED - den ska
        # hissas upp som vanligt OCH sedan prunas bort som lövnod, medan
        # kedjan i övrigt renderas normalt.
        axe = make_axe()
        comment = None
        chain = []
        for i in range(Comment.MAX_DEPTH + 3):
            status = "REJECTED" if i == Comment.MAX_DEPTH + 2 else "APPROVED"
            comment = Comment.objects.create(
                axe=axe, parent=comment, body=f"Nivå {i}", status=status
            )
            chain.append(comment)

        tree = build_comment_tree(axe, is_staff=False)

        node = tree[0]
        for _ in range(Comment.MAX_DEPTH):
            node = node.rendered_children[0]

        # Två svar hissas hit (index MAX_DEPTH+1), det sista (REJECTED,
        # lövnod) ska vara pruned bort.
        hoisted_survivor = chain[Comment.MAX_DEPTH + 1]
        self.assertEqual([c.pk for c in node.rendered_children], [hoisted_survivor.pk])


class CommentTreeRenderingTest(TestCase):
    def test_reply_renders_nested_with_replies_wrapper_and_line_class(self):
        axe = make_axe()
        root = Comment.objects.create(axe=axe, body="Rotkommentar", status="APPROVED")
        Comment.objects.create(
            axe=axe, parent=root, body="Svarskommentar", status="APPROVED"
        )

        response = self.client.get(reverse("axe_detail", args=[axe.pk]))
        content = response.content.decode()

        self.assertIn("Rotkommentar", content)
        self.assertIn("Svarskommentar", content)
        self.assertIn('class="list-unstyled replies lvl1"', content)

    def test_anonymous_sees_stub_for_removed_comment_with_reply(self):
        axe = make_axe()
        parent = Comment.objects.create(
            axe=axe, body="Ursprunglig text", status="APPROVED", is_removed=True
        )
        Comment.objects.create(
            axe=axe, parent=parent, body="Svar som lever kvar", status="APPROVED"
        )

        response = self.client.get(reverse("axe_detail", args=[axe.pk]))
        content = response.content.decode()

        self.assertNotIn("Ursprunglig text", content)
        self.assertIn("Kommentaren har tagits bort.", content)
        self.assertIn("Svar som lever kvar", content)

    def test_anonymous_sees_pending_stub_with_neutral_text(self):
        axe = make_axe()
        parent = Comment.objects.create(axe=axe, body="Väntar", status="PENDING")
        Comment.objects.create(
            axe=axe, parent=parent, body="Godkänt barn", status="APPROVED"
        )

        response = self.client.get(reverse("axe_detail", args=[axe.pk]))
        content = response.content.decode()

        self.assertNotIn("<p>Väntar</p>", content)
        self.assertIn("En kommentar väntar på granskning här.", content)

    def test_staff_sees_inline_moderation_with_contextual_buttons(self):
        user = User.objects.create_user(username="admin", password="pass1234")
        self.client.force_login(user)
        axe = make_axe()
        Comment.objects.create(axe=axe, body="Väntande kommentar", status="PENDING")

        response = self.client.get(reverse("axe_detail", args=[axe.pk]))
        content = response.content.decode()

        self.assertIn("Väntande kommentar", content)
        self.assertIn("Godkänn", content)
        self.assertIn("Avvisa", content)
        self.assertIn("Skräp", content)
        self.assertIn("Ta bort", content)

    def test_staff_does_not_see_approve_button_on_already_approved_comment(self):
        user = User.objects.create_user(username="admin", password="pass1234")
        self.client.force_login(user)
        axe = make_axe()
        Comment.objects.create(axe=axe, body="Redan godkänd", status="APPROVED")

        response = self.client.get(reverse("axe_detail", args=[axe.pk]))
        content = response.content.decode()

        self.assertNotIn("Godkänn", content)
        self.assertIn("Ta bort", content)

    def test_anonymous_sees_no_moderation_buttons(self):
        axe = make_axe()
        Comment.objects.create(axe=axe, body="Godkänd kommentar", status="APPROVED")

        response = self.client.get(reverse("axe_detail", args=[axe.pk]))
        content = response.content.decode()

        self.assertNotIn("inline-moderate-btn", content)


class SubmitAxeCommentTest(TestCase):
    def setUp(self):
        cache.clear()
        self.axe = make_axe()
        self.url = reverse("submit_axe_comment", args=[self.axe.pk])

    def tearDown(self):
        cache.clear()

    def test_submit_creates_pending_comment(self):
        response = self.client.post(
            self.url, {"author_name": "Kalle", "body": "Fin yxa!", "website": ""}
        )
        self.assertEqual(response.status_code, 302)
        comment = Comment.objects.get(axe=self.axe)
        self.assertEqual(comment.status, "PENDING")
        self.assertEqual(comment.body, "Fin yxa!")

    def test_authenticated_user_comment_is_auto_approved(self):
        user = User.objects.create_user(username="admin", password="pass1234")
        self.client.force_login(user)

        response = self.client.post(
            self.url, {"author_name": "Admin", "body": "Egen kommentar", "website": ""}
        )
        self.assertEqual(response.status_code, 302)
        comment = Comment.objects.get(axe=self.axe)
        self.assertEqual(comment.status, "APPROVED")
        self.assertEqual(comment.moderated_by, user)
        self.assertIsNotNone(comment.moderated_at)

    def test_pending_comment_not_visible_on_axe_detail(self):
        self.client.post(
            self.url,
            {"author_name": "Kalle", "body": "Väntande kommentar", "website": ""},
        )
        response = self.client.get(reverse("axe_detail", args=[self.axe.pk]))
        self.assertNotIn(b"V\xc3\xa4ntande kommentar", response.content)

    def test_approved_comment_visible_on_axe_detail(self):
        comment = Comment.objects.create(
            axe=self.axe, body="Godkänd kommentar", status="APPROVED"
        )
        response = self.client.get(reverse("axe_detail", args=[self.axe.pk]))
        self.assertIn("Godkänd kommentar".encode(), response.content)
        self.assertEqual([c.pk for c in response.context["comment_tree"]], [comment.pk])

    def test_rejected_and_spam_comments_not_visible(self):
        Comment.objects.create(axe=self.axe, body="Avvisad text", status="REJECTED")
        Comment.objects.create(axe=self.axe, body="Skräptext", status="SPAM")
        response = self.client.get(reverse("axe_detail", args=[self.axe.pk]))
        self.assertNotIn("Avvisad text".encode(), response.content)
        self.assertNotIn("Skräptext".encode(), response.content)

    def test_honeypot_filled_marks_spam_but_returns_success(self):
        response = self.client.post(
            self.url,
            {
                "author_name": "Bot",
                "body": "Köp billiga skor",
                "website": "http://spam.com",
            },
        )
        self.assertEqual(response.status_code, 302)
        comment = Comment.objects.get(axe=self.axe)
        self.assertEqual(comment.status, "SPAM")

    def test_honeypot_ajax_returns_same_success_response_as_normal(self):
        normal = self.client.post(
            self.url,
            {"author_name": "A", "body": "Normal kommentar", "website": ""},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        cache.clear()
        honeypot = self.client.post(
            self.url,
            {"author_name": "B", "body": "Bot-kommentar", "website": "spam"},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(normal.status_code, 200)
        self.assertEqual(honeypot.status_code, 200)
        self.assertEqual(normal.json(), honeypot.json())

    def test_rate_limit_blocks_after_max_submits(self):
        for i in range(5):
            self.client.post(
                self.url, {"author_name": "X", "body": f"Kommentar {i}", "website": ""}
            )
        self.assertEqual(Comment.objects.filter(axe=self.axe).count(), 5)

        self.client.post(
            self.url, {"author_name": "X", "body": "Sjätte kommentaren", "website": ""}
        )
        self.assertEqual(Comment.objects.filter(axe=self.axe).count(), 5)

    def test_comments_disabled_rejects_submission(self):
        settings = Settings.get_settings()
        settings.comments_enabled_public = False
        settings.save()

        self.client.post(
            self.url, {"author_name": "X", "body": "Ska inte sparas", "website": ""}
        )
        self.assertEqual(Comment.objects.filter(axe=self.axe).count(), 0)

    def test_xss_in_comment_body_is_escaped(self):
        Comment.objects.create(
            axe=self.axe, body="<script>alert(1)</script>", status="APPROVED"
        )
        response = self.client.get(reverse("axe_detail", args=[self.axe.pk]))
        content = response.content.decode()
        self.assertNotIn("<script>alert(1)</script>", content)
        self.assertIn("&lt;script&gt;", content)


class SubmitReplyCommentTest(TestCase):
    def setUp(self):
        cache.clear()
        self.axe = make_axe()
        self.url = reverse("submit_axe_comment", args=[self.axe.pk])

    def tearDown(self):
        cache.clear()

    def test_anonymous_can_reply_to_approved_comment(self):
        parent = Comment.objects.create(axe=self.axe, body="Rot", status="APPROVED")

        response = self.client.post(
            self.url,
            {
                "author_name": "Kalle",
                "body": "Ett svar",
                "website": "",
                "parent_id": parent.pk,
            },
        )

        self.assertEqual(response.status_code, 302)
        reply = Comment.objects.get(body="Ett svar")
        self.assertEqual(reply.status, "PENDING")
        self.assertEqual(reply.parent_id, parent.pk)
        self.assertEqual(reply.axe_id, self.axe.pk)
        self.assertEqual(reply.depth, 1)

    def test_anonymous_cannot_reply_to_pending_comment(self):
        parent = Comment.objects.create(axe=self.axe, body="Väntar", status="PENDING")

        response = self.client.post(
            self.url,
            {
                "author_name": "Kalle",
                "body": "Ett svar",
                "website": "",
                "parent_id": parent.pk,
            },
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(Comment.objects.filter(body="Ett svar").exists())

    def test_anonymous_cannot_reply_to_rejected_comment(self):
        parent = Comment.objects.create(axe=self.axe, body="Avvisad", status="REJECTED")

        response = self.client.post(
            self.url,
            {
                "author_name": "Kalle",
                "body": "Ett svar",
                "website": "",
                "parent_id": parent.pk,
            },
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(Comment.objects.filter(body="Ett svar").exists())

    def test_anonymous_cannot_reply_to_removed_comment(self):
        parent = Comment.objects.create(
            axe=self.axe, body="Borttagen", status="APPROVED", is_removed=True
        )

        response = self.client.post(
            self.url,
            {
                "author_name": "Kalle",
                "body": "Ett svar",
                "website": "",
                "parent_id": parent.pk,
            },
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(Comment.objects.filter(body="Ett svar").exists())

    def test_reply_with_parent_from_another_target_is_rejected(self):
        other_axe = make_axe()
        parent = Comment.objects.create(
            axe=other_axe, body="Annan yxas kommentar", status="APPROVED"
        )

        response = self.client.post(
            self.url,
            {
                "author_name": "Kalle",
                "body": "Ett svar",
                "website": "",
                "parent_id": parent.pk,
            },
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(Comment.objects.filter(body="Ett svar").exists())

    def test_reply_with_nonexistent_parent_is_rejected(self):
        response = self.client.post(
            self.url,
            {
                "author_name": "Kalle",
                "body": "Ett svar",
                "website": "",
                "parent_id": 999999,
            },
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(Comment.objects.filter(body="Ett svar").exists())

    def test_authenticated_user_can_reply_to_pending_comment_and_is_auto_approved(
        self,
    ):
        user = User.objects.create_user(username="admin", password="pass1234")
        self.client.force_login(user)
        parent = Comment.objects.create(axe=self.axe, body="Väntar", status="PENDING")

        response = self.client.post(
            self.url,
            {
                "author_name": "Admin",
                "body": "Adminsvar",
                "website": "",
                "parent_id": parent.pk,
            },
        )

        self.assertEqual(response.status_code, 302)
        reply = Comment.objects.get(body="Adminsvar")
        self.assertEqual(reply.status, "APPROVED")
        self.assertEqual(reply.parent_id, parent.pk)
        self.assertEqual(reply.depth, 1)
        self.assertEqual(reply.moderated_by, user)


class SubmitManufacturerCommentTest(TestCase):
    def setUp(self):
        cache.clear()
        self.manufacturer = make_manufacturer()

    def tearDown(self):
        cache.clear()

    def test_approved_comment_visible_on_manufacturer_detail(self):
        Comment.objects.create(
            manufacturer=self.manufacturer,
            body="Godkänd tillverkarkommentar",
            status="APPROVED",
        )
        response = self.client.get(
            reverse("manufacturer_detail", args=[self.manufacturer.pk])
        )
        self.assertIn("Godkänd tillverkarkommentar".encode(), response.content)

    def test_submit_creates_pending_manufacturer_comment(self):
        url = reverse("submit_manufacturer_comment", args=[self.manufacturer.pk])
        response = self.client.post(
            url, {"author_name": "Kalle", "body": "Fin tillverkare!", "website": ""}
        )
        self.assertEqual(response.status_code, 302)
        comment = Comment.objects.get(manufacturer=self.manufacturer)
        self.assertEqual(comment.status, "PENDING")


class SubmitStampCommentTest(TestCase):
    def setUp(self):
        cache.clear()
        self.stamp = make_stamp()
        self.url = reverse("submit_stamp_comment", args=[self.stamp.pk])

    def tearDown(self):
        cache.clear()

    def test_submit_creates_pending_comment_not_visible_on_stamp_detail(self):
        response = self.client.post(
            self.url,
            {
                "author_name": "Kalle",
                "body": "Väntande stämpelkommentar",
                "website": "",
            },
        )
        self.assertEqual(response.status_code, 302)
        comment = Comment.objects.get(stamp=self.stamp)
        self.assertEqual(comment.status, "PENDING")

        detail_response = self.client.get(reverse("stamp_detail", args=[self.stamp.pk]))
        self.assertNotIn("Väntande stämpelkommentar".encode(), detail_response.content)

    def test_approved_comment_visible_on_stamp_detail(self):
        Comment.objects.create(
            stamp=self.stamp, body="Godkänd stämpelkommentar", status="APPROVED"
        )
        response = self.client.get(reverse("stamp_detail", args=[self.stamp.pk]))
        self.assertIn("Godkänd stämpelkommentar".encode(), response.content)


class CommentModerationViewTest(TestCase):
    def setUp(self):
        cache.clear()
        self.axe = make_axe()

    def tearDown(self):
        cache.clear()

    def test_moderation_view_requires_login(self):
        response = self.client.get(reverse("comment_moderation"))
        self.assertEqual(response.status_code, 302)

    def test_moderate_comment_approve(self):
        user = User.objects.create_user(username="admin", password="pass1234")
        self.client.force_login(user)
        comment = Comment.objects.create(axe=self.axe, body="Väntar på beslut")

        response = self.client.post(
            reverse("moderate_comment", args=[comment.pk]), {"action": "approve"}
        )
        self.assertEqual(response.status_code, 200)

        comment.refresh_from_db()
        self.assertEqual(comment.status, "APPROVED")
        self.assertEqual(comment.moderated_by, user)
        self.assertIsNotNone(comment.moderated_at)

    def test_delete_comment_with_replies_becomes_tombstone_not_deleted(self):
        user = User.objects.create_user(username="admin", password="pass1234")
        self.client.force_login(user)
        parent = Comment.objects.create(axe=self.axe, body="Rot", status="APPROVED")
        Comment.objects.create(
            axe=self.axe, parent=parent, body="Svar", status="APPROVED"
        )

        response = self.client.post(
            reverse("moderate_comment", args=[parent.pk]), {"action": "delete"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"success": True, "removed": True})

        parent.refresh_from_db()
        self.assertTrue(parent.is_removed)
        self.assertEqual(parent.moderated_by, user)
        self.assertIsNotNone(parent.moderated_at)
        self.assertTrue(Comment.objects.filter(pk=parent.pk).exists())

    def test_delete_leaf_comment_is_actually_deleted(self):
        user = User.objects.create_user(username="admin", password="pass1234")
        self.client.force_login(user)
        comment = Comment.objects.create(
            axe=self.axe, body="Ensam kommentar", status="APPROVED"
        )

        response = self.client.post(
            reverse("moderate_comment", args=[comment.pk]), {"action": "delete"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"success": True, "deleted": True})
        self.assertFalse(Comment.objects.filter(pk=comment.pk).exists())
