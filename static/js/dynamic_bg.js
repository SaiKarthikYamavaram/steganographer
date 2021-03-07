function change_bg(file) {
	console.log(file);
	try {
		document.getElementById("blah").src = "URL(" + file + ")";
		document.getElementById("blah").visibility = "visible";
	} catch (error) {
		console.log(error);
	}
}
// onchange="document.getElementById('blah').style.background ='URL($`window.URL.createObjectURL(this.files[0]`))'
