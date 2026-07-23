"""Trädbygge för kommentarer - delas av axe_detail, manufacturer_detail och
stamp_detail så att alla tre detaljvyer använder samma logik (se
tradade-kommentarer-design.md kap 2 och 7, fas 1)."""

from axes.models import Comment


def _attach_rendered_children(node, children_by_parent, real_depth):
    """Sätter node.rendered_children rekursivt.

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


def build_approved_comment_tree(target):
    """Bygg det godkända kommentarsträdet för ett mål (yxa/tillverkare/stämpel).

    En (1) platt query - trädet byggs i Python, ingen N+1. Toppnivå
    nyast-först, svar inom en tråd kronologiskt (äldst-först). Svar djupare
    än Comment.MAX_DEPTH hissas upp till strukturella syskon på sista
    synliga nivån, se _attach_rendered_children.
    """
    comments = list(
        target.comments.filter(status="APPROVED")
        .select_related("moderated_by")
        .order_by("created_at")
    )

    children_by_parent = {}
    for comment in comments:
        children_by_parent.setdefault(comment.parent_id, []).append(comment)

    roots = children_by_parent.get(None, [])
    roots.reverse()

    for root in roots:
        _attach_rendered_children(root, children_by_parent, real_depth=0)

    return roots
