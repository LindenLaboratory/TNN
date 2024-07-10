document.getElementById("save-btn").addEventListener("click", function() {
    var title = document.getElementById("title").value;
    var content = document.getElementById("notepad").value;

    // Create a new XMLHttpRequest object
    var xhr = new XMLHttpRequest();

    // Configure the request
    xhr.open("POST", "/save", true);
    xhr.setRequestHeader("Content-Type", "application/json");

    // Define the data to be sent
    var data = JSON.stringify({ title: title, content: content });

    // Handle the response
    xhr.onreadystatechange = function() {
        if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
            // Handle the response from the Flask route
            var response = JSON.parse(xhr.responseText);
            console.log(response);
        }
    };

    // Send the request with the data
    xhr.send(data);
});
