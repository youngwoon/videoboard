# videoboard

Simple http server for visualizing videos and images.

![Screenshot: videoboard](screenshot.png)

## Usage

Run videoboard:
```
$ videoboard
```

Check the website at `http://127.0.0.1:8000` or `http://[server]:[port]`.

Whenever click a directory, videoboard reloads videos and images inside the directory.

Options:

* `--logdir`           : Directory where videoboard will look for videos and images recursively
* `--port`             : Port number
* `--height`           : Maximum height of image/video
* `--width`            : Maximum width of image/video
* `--file_name_length` : Maximum length of file name shown in videoboard


## Installation

```
git clone https://github.com/youngwoon/videoboard.git
cd videoboard
pip install -e .
```

## License

[MIT License](LICENSE)

