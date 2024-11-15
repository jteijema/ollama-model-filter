# Model Size Filter

Model Size Filter is a web application that allows users to filter and explore machine learning models by size. The models are scraped from [Ollama](https://ollama.com/) and include details such as available sizes and the last updated time. The app provides an interactive slider for refining results and links models to their respective detail pages.

![image](https://github.com/user-attachments/assets/1d1abe9d-c665-4bbc-b0b4-833cf7605061)

## Features

- Filter machine learning models by size (e.g., `1b`, `2b`).
- View model details, including available sizes and last updated time.
- Interactive slider for filtering models.
- Models are linked to their pages on Ollama.

## Running the Application

Pull and run the Docker container:
```
docker pull ghcr.io/jteijema/ollama-model-size-filter:latest
docker run -p 5000:5000 -d --name ollama-models-filter -e FLASK_RUN_HOST=0.0.0.0 -e FLASK_RUN_PORT=5000 ghcr.io/jteijema/ollama-model-size-filter:latest
```
Visit the application in your browser at:

`http://localhost:5000`

## License

This project is licensed under the `MIT License`. See the `LICENSE` file for details.
