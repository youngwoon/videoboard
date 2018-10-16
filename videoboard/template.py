# Template HTML code for header and script

header = '''
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body {
    font-family: system-ui;
}

.accordion {
    background-color: #eee;
    color: #444;
    cursor: pointer;
    padding: 18px;
    width: 100%;
    border: none;
    text-align: left;
    outline: none;
    font-size: 20px;
    transition: 0.4s;
}

.active, .accordion:hover {
    background-color: #ccc;
}

.accordion:after {
    content: "\\02795";
    font-size: 15px;
    color: #777;
    float: right;
    margin-left: 5px;
}

.active:after {
    content: "\\2796";
}

.panel {
    padding: 0 18px;
    background-color: white;
    overflow: hidden;
    display: none;
    flex-wrap: wrap;
    flex-direction: row;
}

.flex-item {
    padding: 5px 10px;
    text-align: center;
    font-size: 20px;
    line-height: 1.5;
}

img, video {
    max-height: 320px;
    max-width: 320px;
    height: auto;
    width: auto;
}

</style>
</head>
'''


script = '''
<script type="text/javascript" src="https://ajax.googleapis.com/ajax/libs/jquery/1.7.2/jquery.min.js"></script>
<script type="text/javascript">

var accordions = document.getElementsByClassName("accordion");

for (var i = 0; i < accordions.length; i++) {
    var acc = accordions[i];
    acc.addEventListener("click", function() {
        this.classList.toggle("active");
        var currentAcc = this;
        var panel = this.nextElementSibling;
        if (panel.style.display === "flex") {
            panel.style.display = "none";
        } else {
            panel.style.display = "flex";
            var url = "";
            var message = this.innerHTML.split("\\n")[1];

            $.post(url, message).done(function(data) {
                var htmlOld = currentAcc.innerHTML;
                var htmlNew = htmlOld.replace(/\\[[\\d*] items\\]$/im,
                    "[" + data.length + " items]");
                currentAcc.innerHTML = htmlNew;

                while (panel.firstChild) {
                    panel.removeChild(panel.firstChild);
                }

                var itemHTML;
                for (var j = 0; j < data.length; j++) {
                    var newItem = document.createElement('div');
                    var ext = data[j]["path"].split('.').pop();
                    if (ext == "mp4") {
                        itemHTML = "<video src=\\"" + data[j]["path"] +
                            "\\" controls type=\\"video/mp4\\"></video>";
                    } else {
                        itemHTML = "<img src=\\"" + data[j]["path"] +
                            "\\"></img>";
                    }

                    var fileName = data[j]["name"];
                    var fileNameLength = fileName.length;
                    var maxLength = 30;
                    if (fileNameLength > maxLength) {
                        fileName = fileName.substring(0, maxLength - 10) + "..." +
                            fileName.substring(fileNameLength - 7);
                    }

                    newItem.className = "flex-item";
                    newItem.innerHTML = "<a href=\\"" + data[j]["path"] + "\\">" +
                        fileName + "</a><br>" +
                        data[j]["time"] + "<br>" + itemHTML;
                    panel.appendChild(newItem);
                }
            });
        }
    });
}
</script>
'''
