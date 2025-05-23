if __name__ == "__main__":
    import app
    pp = app.create_app_with_blueprint()
    pp.run(debug=True, host="0.0.0.0")