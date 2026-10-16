from engine.connection_manager import create_session


def test_connection():

    session = None

    try:
        session = create_session()

        print("Snowflake connection successful.")
        print("Snowflake session established successfully.")

    except Exception as e:
        print(f"Snowflake connection test failed: {type(e).__name__}: {e}")

    finally:
        if session is not None:
            session.close()
            print("Snowflake session closed.")


if __name__ == "__main__":
    test_connection()