if (!window.dash_clientside) {
    window.dash_clientside = {};
}

const baseHref = "/home/dataset/";

// create the "ui" namespace within dash_clientside
window.dash_clientside.ui = {
    // this function can be called by the python library
    jsFunction: function(elmntId) {	
		try  {
			if (elmntId) {
				var scrollToElmnt = document.getElementById(elmntId);
				scrollToElmnt.scrollIntoView();			
			} else {
				window.scrollTo(0,0);
			}
		}
		catch (err) {
			console.log('Error scrollIntoView_Menu : ' + err);
		}
    },
	
	updateThemeColor : function(newThemeBackgroundColor, newThemeColor) {
		var bodyStyles = document.body.style;
		bodyStyles.setProperty('--theme-background-color', newThemeBackgroundColor);
		bodyStyles.setProperty('--theme-color', newThemeColor);
	},

	executeSearchRequest : function(newValue) {
		if(newValue)
		{
			let newValueConst = newValue;
			const newValueSplit = newValue.split('-');
			if(newValueConst == "tab-menu-link-2") {
				var button = document.getElementById("menu-link-2");
				button.click();
			} else if(newValueConst == "tab-menu-link-3") {
				var button = document.getElementById("menu-link-3");
				button.click();
			} else if (newValueConst == "tab-menu-link-4") {
				var button = document.getElementById("menu-link-4");
				button.click();
			} else if (newValueConst == "tab-menu-link-5") {
				var button = document.getElementById("menu-link-5");
				button.click();
			} else if (newValueSplit[0] == "class") {
				var button = document.getElementById("menu-link-3");
				button.click();
				var buttonString = '{"button-type":"select-classes-button","class-id":' + newValueSplit[1] + '}';
				setTimeout(function() {
					button = document.getElementById(buttonString);
					button.click();
				}, 900);
			} else if (newValueSplit[0] == "student") {
				var button = document.getElementById("menu-link-4");
				button.click();
				var buttonString = '{"button-type":"students-select-classes-button","class-id":' + newValueSplit[1] + '}';
				setTimeout(function() {
					button = document.getElementById(buttonString);
					button.click();
					buttonString = '{"button-type":"students-select-student-button","student-id":' + newValueSplit[2] + '}';
					setTimeout(function() {
						button = document.getElementById(buttonString);
						button.click();
					}, 900);
				}, 900);
			}
		}
        return "Learning Analytics Web Application";
    },
}