from zotero_utils import get_listbibl, update_listbibl


list_bibl = "./out/listbibl_static.xml"

new_doc = update_listbibl(get_listbibl(limit="500"), orig_file=list_bibl)
new_doc.tree_to_file(list_bibl)
