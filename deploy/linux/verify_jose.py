try:
    from jose import JWK
    print("JWK import OK")
except ImportError as e:
    print(f"JWK import FAILED: {e}")
    try:
        from jose import jwt, JWTError, ExpiredSignatureError
        print("jwt/JWTError/ExpiredSignatureError import OK")
    except ImportError as e2:
        print(f"jwt import also FAILED: {e2}")