from app import create_app_with_blueprint

app = create_app_with_blueprint()

if __name__ == "__main__":
    app.run(debug=True)
