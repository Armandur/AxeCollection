from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from . import views_axe
from . import views_contact
from . import views_manufacturer
from . import views_transaction
from . import views_platform
from . import views_stamp

urlpatterns = [
    path("", views_axe.axe_list, name="axe_list"),
    path("yxor/", views_axe.axe_list, name="axe_list"),
    path("yxor/ny/", views_axe.axe_create, name="axe_create"),
    path("yxor/<int:pk>/", views_axe.axe_detail, name="axe_detail"),
    path("yxor/<int:pk>/redigera/", views_axe.axe_edit, name="axe_edit"),
    path(
        "yxor/<int:pk>/mottagning/",
        views_axe.receiving_workflow,
        name="receiving_workflow",
    ),
    path("yxor/<int:pk>/matt/", views_axe.add_measurement, name="add_measurement"),
    path(
        "yxor/<int:pk>/matt/mall/",
        views_axe.add_measurements_from_template,
        name="add_measurements_from_template",
    ),
    path(
        "yxor/<int:pk>/matt/<int:measurement_id>/",
        views_axe.delete_measurement,
        name="delete_measurement",
    ),
    path(
        "yxor/<int:pk>/matt/<int:measurement_id>/update/",
        views_axe.update_measurement,
        name="update_measurement",
    ),
    path(
        "yxor/<int:pk>/status/", views_axe.update_axe_status, name="update_axe_status"
    ),
    path("galleri/", views_axe.axe_gallery, name="axe_gallery"),
    path("galleri/<int:pk>/", views_axe.axe_gallery, name="axe_gallery_detail"),
    path("kontakter/", views_contact.contact_list, name="contact_list"),
    path("kontakter/ny/", views_contact.contact_create, name="contact_create"),
    path("kontakter/<int:pk>/", views_contact.contact_detail, name="contact_detail"),
    path(
        "kontakter/<int:pk>/redigera/", views_contact.contact_edit, name="contact_edit"
    ),
    path(
        "kontakter/<int:pk>/ta-bort/",
        views_contact.contact_delete,
        name="contact_delete",
    ),
    path(
        "tillverkare/", views_manufacturer.manufacturer_list, name="manufacturer_list"
    ),
    path(
        "tillverkare/ny/",
        views_manufacturer.manufacturer_create,
        name="manufacturer_create",
    ),
    path(
        "tillverkare/<int:pk>/redigera/",
        views_manufacturer.manufacturer_edit,
        name="manufacturer_edit",
    ),
    path(
        "tillverkare/<int:pk>/",
        views_manufacturer.manufacturer_detail,
        name="manufacturer_detail",
    ),
    path(
        "tillverkare/<int:pk>/redigera-information/",
        views_manufacturer.edit_manufacturer_information,
        name="edit_manufacturer_information",
    ),
    path(
        "tillverkare/<int:pk>/redigera-namn/",
        views_manufacturer.edit_manufacturer_name,
        name="edit_manufacturer_name",
    ),
    path(
        "tillverkare/bild/<int:image_id>/redigera/",
        views_manufacturer.edit_manufacturer_image,
        name="edit_manufacturer_image",
    ),
    path(
        "tillverkare/bild/<int:image_id>/ta-bort/",
        views_manufacturer.delete_manufacturer_image,
        name="delete_manufacturer_image",
    ),
    path(
        "tillverkare/bild/lagg-till/",
        views_manufacturer.add_manufacturer_image,
        name="add_manufacturer_image",
    ),
    path(
        "tillverkare/bild/ordning/",
        views_manufacturer.reorder_manufacturer_images,
        name="reorder_manufacturer_images",
    ),
    path(
        "tillverkare/lank/<int:link_id>/redigera/",
        views_manufacturer.edit_manufacturer_link,
        name="edit_manufacturer_link",
    ),
    path(
        "tillverkare/lank/<int:link_id>/ta-bort/",
        views_manufacturer.delete_manufacturer_link,
        name="delete_manufacturer_link",
    ),
    path(
        "tillverkare/lank/lagg-till/",
        views_manufacturer.add_manufacturer_link,
        name="add_manufacturer_link",
    ),
    path(
        "tillverkare/lank/ordning/",
        views_manufacturer.reorder_manufacturer_links,
        name="reorder_manufacturer_links",
    ),
    path(
        "tillverkare/<int:pk>/ta-bort/",
        views_manufacturer.delete_manufacturer,
        name="delete_manufacturer",
    ),
    path(
        "tillverkare/dropdown/",
        views_manufacturer.get_manufacturers_for_dropdown,
        name="get_manufacturers_for_dropdown",
    ),
    path(
        "tillverkare/check-name/",
        views_manufacturer.check_manufacturer_name,
        name="check_manufacturer_name",
    ),
    path("transaktioner/", views_transaction.transaction_list, name="transaction_list"),
    path(
        "api/transaction/<int:pk>/",
        views_transaction.api_transaction_detail,
        name="api_transaction_detail",
    ),
    path(
        "api/transaction/<int:pk>/update/",
        views_transaction.api_transaction_update,
        name="api_transaction_update",
    ),
    path(
        "api/transaction/<int:pk>/delete/",
        views_transaction.api_transaction_delete,
        name="api_transaction_delete",
    ),
    # Plattformar
    path("plattformar/", views_platform.platform_list, name="platform_list"),
    path("plattformar/ny/", views_platform.platform_create, name="platform_create"),
    path(
        "plattformar/<int:pk>/", views_platform.platform_detail, name="platform_detail"
    ),
    path(
        "plattformar/<int:pk>/redigera/",
        views_platform.platform_edit,
        name="platform_edit",
    ),
    path(
        "plattformar/<int:pk>/ta-bort/",
        views_platform.platform_delete,
        name="platform_delete",
    ),
    path("api/search/contacts/", views.search_contacts, name="search_contacts"),
    path("api/search/platforms/", views.search_platforms, name="search_platforms"),
    path("api/search/global/", views.global_search, name="global_search"),
    path("statistik/", views_axe.statistics_dashboard, name="statistics_dashboard"),
    path(
        "yxor/senaste/info/", views_axe.get_latest_axe_info, name="get_latest_axe_info"
    ),
    path(
        "yxor/senaste/ta-bort/", views_axe.delete_latest_axe, name="delete_latest_axe"
    ),
    path("okopplade-bilder/", views_axe.unlinked_images_view, name="unlinked_images"),
    path(
        "okopplade-bilder/ta-bort/",
        views_axe.delete_unlinked_image,
        name="delete_unlinked_image",
    ),
    path(
        "okopplade-bilder/ladda-ner/",
        views_axe.download_unlinked_images,
        name="download_unlinked_images",
    ),
    # Auth URLs
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="axes/login.html"),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(next_page="/"), name="logout"),
    # Settings
    path("installningar/", views.settings_view, name="settings"),
    # Måttmall-API
    path(
        "api/measurement-templates/",
        views.api_measurement_templates,
        name="api_measurement_templates",
    ),
    path(
        "api/measurement-templates/create/",
        views.api_create_measurement_template,
        name="api_create_measurement_template",
    ),
    path(
        "api/measurement-templates/<int:template_id>/update/",
        views.api_update_measurement_template,
        name="api_update_measurement_template",
    ),
    path(
        "api/measurement-templates/<int:template_id>/delete/",
        views.api_delete_measurement_template,
        name="api_delete_measurement_template",
    ),
    path(
        "api/measurement-types/",
        views.api_measurement_types,
        name="api_measurement_types",
    ),
    path(
        "api/measurement-types/create/",
        views.api_create_measurement_type,
        name="api_create_measurement_type",
    ),
    path(
        "api/measurement-types/<int:type_id>/update/",
        views.api_update_measurement_type,
        name="api_update_measurement_type",
    ),
    path(
        "api/measurement-types/<int:type_id>/delete/",
        views.api_delete_measurement_type,
        name="api_delete_measurement_type",
    ),
    # Stämpelregister URL:er
    path("stamplar/", views_stamp.stamp_list, name="stamp_list"),
    path("stamplar/ny/", views_stamp.stamp_create, name="stamp_create"),
    path("stamplar/<int:stamp_id>/", views_stamp.stamp_detail, name="stamp_detail"),
    path(
        "stamplar/<int:stamp_id>/redigera/", views_stamp.stamp_edit, name="stamp_edit"
    ),
    path("stamplar/sok/", views_stamp.stamp_search, name="stamp_search"),
    path("stamplar/statistik/", views_stamp.stamp_statistics, name="stamp_statistics"),
    path(
        "yxor-utan-stamplar/",
        views_stamp.axes_without_stamps,
        name="axes_without_stamps",
    ),
    path(
        "yxor/<int:axe_id>/stampel/lagg-till/",
        views_stamp.add_axe_stamp,
        name="add_axe_stamp",
    ),
    path(
        "yxor/<int:axe_id>/stampel/<int:axe_stamp_id>/redigera/",
        views_stamp.edit_axe_stamp,
        name="edit_axe_stamp",
    ),
    path(
        "yxor/<int:axe_id>/stampel/<int:axe_stamp_id>/ta-bort/",
        views_stamp.remove_axe_stamp,
        name="remove_axe_stamp",
    ),
    path(
        "stamplar/<int:stamp_id>/bild/lagg-till/",
        views_stamp.stamp_image_upload,
        name="stamp_image_upload",
    ),
    path(
        "stamplar/<int:stamp_id>/bild/<int:image_id>/redigera/",
        views_stamp.stamp_image_edit,
        name="stamp_image_edit",
    ),
    path(
        "stamplar/<int:stamp_id>/bild/<int:image_id>/ta-bort/",
        views_stamp.stamp_image_delete,
        name="stamp_image_delete",
    ),
    # StampImage URL:er (konsoliderade från AxeImageStamp)
    path(
        "yxor/<int:axe_id>/bild/<int:image_id>/markera-stampel/",
        views_stamp.mark_axe_image_as_stamp,
        name="mark_axe_image_as_stamp",
    ),
    path(
        "yxor/<int:axe_id>/bild/<int:image_id>/ta-bort-stampel-markering/",
        views_stamp.unmark_axe_image_stamp,
        name="unmark_axe_image_stamp",
    ),
    path(
        "yxor/<int:axe_id>/stampel-markering/<int:mark_id>/redigera/",
        views_stamp.edit_axe_image_stamp,
        name="edit_axe_image_stamp",
    ),
    path(
        "yxor/<int:axe_id>/bild/<int:image_id>/stampel/redigera-via-axe-stamp/",
        views_stamp.edit_axe_image_stamp_via_axe_stamp,
        name="edit_axe_image_stamp_via_axe_stamp",
    ),
    path(
        "yxor/<int:axe_id>/stampel-markering/<int:mark_id>/ta-bort/",
        views_stamp.remove_axe_image_stamp,
        name="remove_axe_image_stamp",
    ),
    path(
        "stamplar/<int:stamp_id>/beskarning/",
        views_stamp.stamp_image_crop,
        name="stamp_image_crop",
    ),
    path(
        "stamplar/<int:stamp_id>/huvudbild/<int:mark_id>/",
        views_stamp.set_primary_stamp_image,
        name="set_primary_stamp_image",
    ),
    path(
        "yxor/stampel-markering/<int:mark_id>/uppdatera-visa-hela/",
        views_stamp.update_axe_image_stamp_show_full,
        name="update_axe_image_stamp_show_full",
    ),
    # StampTranscription URL:er (endast kopplade till stämplar)
    path(
        "stamplar/<int:stamp_id>/transkriberingar/",
        views_stamp.stamp_transcriptions,
        name="stamp_transcriptions",
    ),
    path(
        "stamplar/<int:stamp_id>/transkriberingar/ny/",
        views_stamp.transcription_create,
        name="stamp_transcription_create",
    ),
    path(
        "stamplar/<int:stamp_id>/transkriberingar/<int:transcription_id>/redigera/",
        views_stamp.transcription_edit,
        name="stamp_transcription_edit",
    ),
    path(
        "stamplar/<int:stamp_id>/transkriberingar/<int:transcription_id>/ta-bort/",
        views_stamp.transcription_delete,
        name="stamp_transcription_delete",
    ),
    # API endpoints
    path(
        "api/stamp-symbols/",
        views_stamp.stamp_symbols_api,
        name="stamp_symbols_api",
    ),
]
