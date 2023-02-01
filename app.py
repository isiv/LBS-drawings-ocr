from website import create_app

app = create_app()

## Run flask application
if __name__ == '__main__':
    app.run(debug=False)