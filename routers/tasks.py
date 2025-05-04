














router = APIRouter(
    prefix="/tasks",
    tags=["tasks"],
)

templates = Jinja2Templates(directory="app/templates")
