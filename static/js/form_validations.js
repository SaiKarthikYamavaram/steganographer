var inp = document.querySelector("#encryption-data");
var key = document.querySelector("#encryption-key");

inp.addEventListener("input", function (event) {
	var inp_req = document.querySelector(".inp-req");
	if (!inp.checkValidity()) {
		console.log("in  here");
		inp_req.style.display = "inline";
	} else {
		console.log("outthere");
		inp_req.style.display = null;
	}
});

key.addEventListener("input", () => {
	if (key.value.length < 24) {
		console.log("less");
	}
});
