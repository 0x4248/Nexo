from fastapi.responses import HTMLResponse
from lib import utils

class Account:
    class Errors:
        def username_length(request, min_length, max_length):
            return HTMLResponse(utils.generate_html(request=request, main_content="Username contains invalid characters."))
        def username_banned(request):
            return HTMLResponse(utils.generate_html(request=request, main_content="Username is banned."))
        def username_exists(request):
            return HTMLResponse(utils.generate_html(request=request, main_content="Username already exists."))
        def username_invalid(request):
            return HTMLResponse(utils.generate_html(request=request, main_content="Username contains invalid characters."))
    
    class Success:
        def user_created(request):
            return HTMLResponse(utils.generate_html(request=request, main_content="User created successfully!"))
        def user_logged_in(request):
            return HTMLResponse(utils.generate_html(request=request, main_content="User logged in successfully!"))
        def user_logged_out(request):
            return HTMLResponse(utils.generate_html(request=request, main_content="User logged out successfully!"))
        def user_deleted(request):
            return HTMLResponse(utils.generate_html(request=request, main_content="User deleted successfully!"))