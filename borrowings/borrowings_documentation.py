from drf_spectacular.utils import OpenApiParameter, OpenApiExample


borrowings_parameters = [
    OpenApiParameter(
        name="is_active",
        type=bool,
        description=("Filter by is_active "
                     "(available inputs: true, True, TRUE, 1 or "
                     "false, False, FALSE, 0) (e.g. ?is_active=true)"),
    ),
    OpenApiParameter(
        name="user_id",
        type=int,
        description="Filter by user_id (e.g. ?user_id=1), works only for admins",
    ),
]

borrowings_examples = [
    OpenApiExample(
        name="Filter by active or inactive borrowings",
        description="Get borrowings that aren or aren't returned.",
        value="?is_active=true",
    ),
    OpenApiExample(
        name="Filter borrowings by user_id",
        description="Get borrowings of specific user(works only for admins).",
        value="?user_id=1",
    ),
]
