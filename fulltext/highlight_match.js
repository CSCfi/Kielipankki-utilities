
// JavaScript code for implementing the highlighting of matching words
// (tokens) within a matched sentence in the fulltext HTML pages of
// the LA murre corpus.
//
// The code assumes in the page URL a fragment identifier containing
// the id of the matched sentence and a query string of the form
// "<i1>-<i2>" where <i1> is the 1-based index of the first word of
// the match and <i2> that of its last word. Each word (token) is
// assumed to have an id of the form "<sid>w<n>" where <sid> is the
// sentence id and n the number of the token in the sentence.
//
// The code adds the class "match" to the matched words.
//
// In order to work, the code needs to be included at the *bottom* of
// a fulltext HTML page.
//
// It should be possible to use code on the fulltext HTML pages of
// other corpora as well.


if (window.location.search && window.location.hash) {
    var hash = window.location.hash.slice(1);
    var pos = window.location.search.slice(1).split("-");
    console.log(window.location.search, hash, pos);
    var start = parseInt(pos[0]);
    var end = parseInt(pos[1]);
    for (var i = start; i <= end; i++) {
	var id = hash + "w" + i.toString();
	console.log(id);
	var elem = document.getElementById(id);
	if (elem) {
	    elem.className += " match";
	}
    }
}
