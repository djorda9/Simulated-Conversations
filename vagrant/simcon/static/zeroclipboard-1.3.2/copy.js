/**
 * Created by Daniel on 3/10/14.
 */
var client = new ZeroClipboard( document.getElementById("copy_button"), {
  moviePath: "/static/zeroclipboard-1.3.2/ZeroClipboard.swf"
} );

client.on( "load", function(client) {
  // alert( "movie is loaded" );
     client.on( "complete", function(client, args) {
    // `this` is the element that was clicked
    alert("Copied text to clipboard: " + args.text );
  } );
} );