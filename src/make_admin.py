from lib.database import User

user = input("Enter the username of the admin: ")
role = input("Enter the role of the admin (admin/user): ")
User.Set.user_role(user, role)
print(f"User {user} has been set to {role} role.")