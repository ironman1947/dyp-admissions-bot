from app.config import settings

print("Phone Number ID:", settings.META_PHONE_NUMBER_ID)
print("WABA ID:", settings.META_WABA_ID)
print("App ID:", settings.META_APP_ID)
print("Verify Token:", settings.META_VERIFY_TOKEN)
print("Database URL loaded:", bool(settings.DATABASE_URL))
print("Access Token loaded:", bool(settings.META_ACCESS_TOKEN))
print("App Secret loaded:", bool(settings.META_APP_SECRET))