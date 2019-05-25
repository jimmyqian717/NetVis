var canvas = document.getElementById("canvas");
var sWidth = window.innerWidth;
var sHeight = window.innerHeight;
// canvas.width = sWidth;
// canvas.height = sHeight;
var ctx = canvas.getContext("2d");


ctx.globalAlpha = .1;
//Edge [1,2]
ctx.beginPath();
ctx.moveTo(.35 * sWidth, .15 * sWidth);
ctx.lineTo(.85 *sWidth, .45 * sWidth);
ctx.stroke();
