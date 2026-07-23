"""Trädbygge för kommentarer - delas av axe_detail, manufacturer_detail och
stamp_detail så att alla tre detaljvyer använder samma logik (se
tradade-kommentarer-design.md kap 2, 4 och 7, fas 1-3)."""

from axes.models import Comment


def _attach_rendered_children(node, children_by_parent, real_depth):
    """Sätter node.rendered_children rekursivt, över ALLA kommentarer
    (oavsett status) - synlighets-pruning sker i ett separat steg efteråt,
    se _prune_visibility.

    `real_depth` är det faktiska antalet nivåer från roten, oberoende av
    det klampade `depth`-fältet på modellen (som blir identiskt för alla
    noder från och med Comment.MAX_DEPTH och därför inte kan användas för
    att avgöra var djup-taket faktiskt ligger).

    När `real_depth` når Comment.MAX_DEPTH blir noden en "hiss-plattform":
    samtliga ättlingar, oavsett hur många riktiga nivåer djupare de ligger,
    plattas ut till strukturella syskon här, i kronologisk ordning. `parent`
    i databasen ändras aldrig - bara var noden hamnar i rendered_children.
    """
    if real_depth < Comment.MAX_DEPTH:
        node.rendered_children = children_by_parent.get(node.id, [])
        for child in node.rendered_children:
            _attach_rendered_children(child, children_by_parent, real_depth + 1)
        return

    flattened = []

    def _collect(n):
        for child in children_by_parent.get(n.id, []):
            flattened.append(child)
            _collect(child)

    _collect(node)
    flattened.sort(key=lambda c: c.created_at)
    for child in flattened:
        child.rendered_children = []
    node.rendered_children = flattened


def _prune_visibility(node, is_staff):
    """Bottom-up-pass ovanpå det redan hissade trädet (_attach_rendered_children):
    avgör per nod om den ska renderas i sin helhet, som platshållare (stub)
    eller prunas bort helt - se tradade-kommentarer-design.md kap 4.1.

    Körs EFTER hissningen, inte ihopblandad med den - hissningen är en ren
    omstrukturering baserad på djup, pruning är en ren synlighetsfråga.
    Genom att köra dem i sekvens (hissa allt, pruna sen det hissade trädet)
    får en hissad men dold lövnod pruna bort korrekt, och en hissad synlig
    nod under en dold förfader håller kvar förfadern som stub.

    Returnerar noden (ev. med `is_visible_stub=True`) eller None om noden
    ska prunas bort helt (dold och utan kvarvarande synliga ättlingar).
    """
    pruned_children = []
    for child in node.rendered_children:
        pruned_child = _prune_visibility(child, is_staff)
        if pruned_child is not None:
            pruned_children.append(pruned_child)
    node.rendered_children = pruned_children

    visible = node.status == "APPROVED" or (node.status == "PENDING" and is_staff)
    if node.is_removed or not visible:
        node.is_visible_stub = bool(node.rendered_children)
        if node.is_removed:
            node.stub_reason = "removed"
        elif node.status == "PENDING":
            node.stub_reason = "pending"
        else:
            node.stub_reason = "moderated"
        return node if node.is_visible_stub else None

    node.is_visible_stub = False
    return node


def build_comment_tree(target, is_staff):
    """Bygg hela kommentarsträdet för ett mål (yxa/tillverkare/stämpel),
    med synlighet per nod anpassad efter viewer.

    En (1) platt query - trädet byggs i Python, ingen N+1. Toppnivå
    nyast-först, svar inom en tråd kronologiskt (äldst-först). Svar djupare
    än Comment.MAX_DEPTH hissas upp till strukturella syskon på sista
    synliga nivån (_attach_rendered_children). Dolda noder (PENDING för
    anonym, REJECTED/SPAM, is_removed) bevaras som platshållare om de har
    minst en synlig ättling kvar, annars prunas de bort helt
    (_prune_visibility).

    `is_staff` avgör om PENDING-kommentarer visas i sin helhet (inloggad,
    för inline-moderering) eller döljs bakom en neutral "väntar"-stub.
    """
    comments = list(
        target.comments.select_related("moderated_by").order_by("created_at")
    )

    children_by_parent = {}
    for comment in comments:
        children_by_parent.setdefault(comment.parent_id, []).append(comment)

    roots = children_by_parent.get(None, [])
    roots.reverse()

    for root in roots:
        _attach_rendered_children(root, children_by_parent, real_depth=0)

    pruned_roots = []
    for root in roots:
        pruned_root = _prune_visibility(root, is_staff)
        if pruned_root is not None:
            pruned_roots.append(pruned_root)

    return pruned_roots
