// Initialize Default Properties of Keyboard Interface
// This script can set styles for Rasa Webchat Elements as well
var kbi_init_props = Object();

function KeyboardInterfaceInit(properties) {
    kbi_init_props = properties;
    console.log("keyboard interface props: ", kbi_init_props);
}

$(document).ready(function () {

    // Switch Element
    if (kbi_init_props["disableSwitch"] === false) {
        var switchElement = `
        <div id="kbi_lang_switch" class="invisible container rounded-pill kbi-lsb"
        style="background-color: #135afe; padding: 5px 5px 5px 5px; width: 300px; height: 62px; box-shadow: 2px 6px 10px rgba(0, 0, 0, 0.4);
        position: absolute; ` + kbi_init_props["switchBarPosition"]["hpos"] + `: ` + kbi_init_props["switchBarPosition"]["hval"] + `;  ` + kbi_init_props["switchBarPosition"]["vpos"] + `:  ` + kbi_init_props["switchBarPosition"]["vval"] + `; z-index:  ` + kbi_init_props["switchBarPosition"]["zindex"] + `;">
            <div class="row">
                <div class="col-2 my-auto mx-auto">
                    <h2>⌨️</h2>
                </div>
                <div class="col">
                    <div class="form-check form-switch mt-3 mx-3">
                        <input class="form-check-input" type="checkbox" id="flexSwitchCheckChecked" checked>
                        <label class="form-check-label text-white" for="flexSwitchCheckChecked">
                            Sinhala <span class="text-info"> CTRL+Q </span>
                        </label>
                    </div>
                </div>
            </div>
        </div>
        `

        document.body.innerHTML += switchElement;
        // console.log("switch added!");

        var kbi_styles = document.createElement('style');
        kbi_styles.innerHTML = `
        .form-check-input:checked {
            background-color: ` + kbi_init_props["switchColor"] + `;
            border-color: ` + kbi_init_props["switchColor"] + `;
        }
        .kbi-lsb {
            background-color: ` + kbi_init_props["switchBarColor"] + ` !important;
        }
        `
        document.body.appendChild(kbi_styles);
    }

    // Rasa Webchat Styles
    try {
        if (kbi_init_props["widgetStyles"]["disableRasaWebchatStyles"] === false) {
            var rw_styles = document.createElement('style');
            rw_styles.innerHTML = `
            .rw-launcher {
                background-color: ` + kbi_init_props["widgetStyles"]["widgetLauncherColor"] + ` !important;
                box-shadow: 2px 6px 10px rgba(0, 0, 0, 0.4) !important;
            }
            .rw-header {
                background-color: ` + kbi_init_props["widgetStyles"]["widgetHeaderColor"] + ` !important;
            }
            /*.rw-title {
                font-size: 16px !important;
            }*/
            .rw-sender, .rw-new-message, .rw-send {
                background-color: ` + kbi_init_props["widgetStyles"]["widgetMessageAreaColor"] + ` !important;
                font-color: white;
            }
            .rw-client {
                background-color: ` + kbi_init_props["widgetStyles"]["widgetUserUtteredColor"] + ` !important;
                color: ` + kbi_init_props["widgetStyles"]["widgetUserUtteredTextColor"] + ` !important;
            }
            .rw-reply {
                background-color: ` + kbi_init_props["widgetStyles"]["widgetReplyButtonColor"] + ` !important;
                border-color: ` + kbi_init_props["widgetStyles"]["widgetButtonColor"] + ` !important;
            }
            .rw-response {
                background-color: ` + kbi_init_props["widgetStyles"]["widgetBotUtteredColor"] + ` !important;
                color: ` + kbi_init_props["widgetStyles"]["widgetBotUtteredTextColor"] + ` !important;
            }
            .rw-send  {
                background-image: url(" ` + kbi_init_props["widgetStyles"]["widgetSendMessageImage"] + ` ") !important;
                background-size: ` + kbi_init_props["widgetStyles"]["widgetSendMessageImageSize"]["width"] + ` ` + kbi_init_props["widgetStyles"]["widgetSendMessageImageSize"]["height"] + ` !important;
                background-repeat: no-repeat !important;
            }
            .rw-send > svg {
                visibility: hidden !important;
            }
            .rw-messages-container {
                background-color: ` + kbi_init_props["widgetStyles"]["widgetContainerColor"] + ` !important;
            }
            `
            if (kbi_init_props["widgetStyles"]["widgetMainAvatarImage"] != "") {
                rw_styles.innerHTML += `
                .rw-header > .rw-avatar {
                    content:url("` + kbi_init_props["widgetStyles"]["widgetMainAvatarImage"] + `") !important;
                }
                `
            }

            document.body.appendChild(rw_styles);
        }
        console.log("a custom webchat theme was set.");
    } catch(e) {
        console.log("the default webchat theme was set.");
    }

    // Vowel Keys and Maps
    var sinhala_vowels_keys = [
        'uu', 'oo', 'oe', 'aa', 'AA', 'Aa', 'ae', 'ii', 'ie', 'ee', 'ea', 'ei', 'uu', 'au',
        'O', 'a', 'A', 'i', 'e', 'u', 'U', 'o', 'E', 'I'
    ];
    var sinhala_vowel_pure_map = {
        'uu': 'ඌ', 'oo': 'ඕ', 'oe': 'ඕ', 'aa': 'ආ', 'AA': 'ඈ', 'Aa': 'ඈ', 'ae': 'ඈ', 'ii': 'ඊ', 'ie': 'ඊ', 'ee': 'ඒ', 'ea': 'ඒ', 'ei': 'ඒ', 'uu': 'ඌ', 'au': 'ඖ',
        'O': 'ඖ', 'a': 'අ', 'A': 'ඇ', 'i': 'ඉ', 'e': 'එ', 'u': 'උ', 'U': 'උ', 'o': 'ඔ', 'E': 'ඓ', 'I': 'ඓ'
    };
    var sinhala_vowel_suffix_map = {
        'uu': 'ූ', 'oo': 'ෝ', 'oe': 'ෝ', 'aa': 'ා', 'AA': 'ෑ', 'Aa': 'ෑ', 'ae': 'ෑ', 'ii': 'ී', 'ie': 'ී', 'ee': 'ේ', 'ea': 'ේ', 'ei': 'ේ', 'uu': 'ූ', 'au': 'ෞ',
        'O': 'ෞ', 'a': '', 'A': 'ැ', 'i': 'ි', 'e': 'ෙ', 'u': 'ු', 'o': 'ො', 'E': 'ෛ', 'I': 'ෛ'
    };

    // Non-joining Character Keys and Maps [ + '\u200D']
    var sinhala_nonjoining_keys = [
        'RR', 'z', 'x', 'H', 'R'
    ];
    var sinhala_nonjoining_map = {
        'RR': 'ඎ',
        'z': 'ර්' + '\u200D',
        'x': 'ං',
        'H': 'ඃ',
        'R': 'ඍ'
    };

    // Consonent Keys and Maps
    var sinhala_consonent_keys = [
        'nndh', 'nnd', 'nng', 'mmb',
        'GN', 'KN', 'Lu', 'Th', 'Dh', 'gh', 'Ch', 'ph', 'kh', 'bh',
        'Sh', 'sh', 'dh', 'ch', 'th',
        'N', 'L', 'K', 'G', 'T', 'D', 'P', 'B', 'C', 'X', 'J',
        't', 'k', 'd', 'n', 'p', 'b', 'm', 'M', 'Y', 'y', 'j', 'l', 'v', 'w', 'V', 'W',
        's', 'S', 'h', 'f', 'F', 'g', 'c',
        'r'
    ];
    var sinhala_consonant_map = {
        'nndh': 'ඳ', 'nnd': 'ඬ', 'nng': 'ඟ', 'mmb': 'ඹ',
        'GN': 'ඥ', 'KN': 'ඤ', 'Lu': 'ළු', 'Th': 'ථ', 'Dh': 'ධ', 'gh': 'ඝ', 'Ch': 'ඡ', 'ph': 'ඵ', 'kh': 'ඛ', 'bh': 'භ',
        'Sh': 'ෂ', 'sh': 'ශ', 'dh': 'ද', 'ch': 'ච', 'th': 'ත',
        'N': 'ණ', 'L': 'ළ', 'K': 'ඛ', 'G': 'ඝ', 'T': 'ඨ', 'D': 'ඪ', 'P': 'ඵ', 'B': 'භ', 'C': 'ඡ', 'X': 'ඞ', 'J': 'ඣ',
        't': 'ට', 'k': 'ක', 'd': 'ඩ', 'n': 'න', 'p': 'ප', 'b': 'බ', 'm': 'ම', 'M': 'ම', 'Y': 'ය', 'y': 'ය', 'j': 'ජ', 'l': 'ල', 'v': 'ව', 'w': 'ව', 'V': 'ව', 'W': 'ව',
        's': 'ස', 'S': 'ස', 'h': 'හ', 'f': 'ෆ', 'F': 'ෆ', 'g': 'ග', 'c': 'ච',
        'r': 'ර'
    };
    // consonantsUni[14] = 'ළු'; consonants[14] = 'Lu'; TODO HANDLE THIS SPC

    // Special Character Keys and Maps
    var sinhala_special_keys = [
        'ruu',
        'ru'
    ];
    var sinhala_special_map = {
        'ruu': 'ෲ',
        'ru': 'ෘ'
    };

    // EN-SI Char Converter
    function convert(text) {
        var EN_pattern, SI_pattern, RegEx_pattern;

        // Replacing non-joining characters
        sinhala_nonjoining_keys.forEach((nj_char, idx) => {
            EN_pattern = nj_char;
            SI_pattern = sinhala_nonjoining_map[nj_char];
            RegEx_pattern = new RegExp(EN_pattern, "g");
            text = text.replace(RegEx_pattern, SI_pattern);
        });

        // Replacing special consonents
        sinhala_special_keys.forEach((sp_char, idx) => {
            sinhala_consonent_keys.forEach((con_char, idx) => {
                EN_pattern = con_char + sp_char;
                SI_pattern = sinhala_consonant_map[con_char] + sinhala_special_map[sp_char];
                RegEx_pattern = new RegExp(EN_pattern, "g");
                text = text.replace(RegEx_pattern, SI_pattern);
            });
        });

        // Replacing consonants + Rakaransha + vowel modifiers
        sinhala_consonent_keys.forEach((con_char, idx) => {
            sinhala_vowels_keys.forEach((v_char, idx) => {
                EN_pattern = con_char + "r" + v_char;
                SI_pattern = sinhala_consonant_map[con_char] + "්‍ර" + sinhala_vowel_suffix_map[v_char];
                RegEx_pattern = new RegExp(EN_pattern, "g");
                text = text.replace(RegEx_pattern, SI_pattern);
            });
            EN_pattern = con_char + "r";
            SI_pattern = sinhala_consonant_map[con_char] + "්‍ර";
            RegEx_pattern = new RegExp(EN_pattern, "g");
            text = text.replace(RegEx_pattern, SI_pattern);
        });

        // Replacing consonents + vowel modifiers
        sinhala_consonent_keys.forEach((con_char, idx) => {
            sinhala_vowels_keys.forEach((v_char, idx) => {
                EN_pattern = con_char + v_char;
                SI_pattern = sinhala_consonant_map[con_char] + sinhala_vowel_suffix_map[v_char];
                RegEx_pattern = new RegExp(EN_pattern, "g");
                text = text.replace(RegEx_pattern, SI_pattern);
            });
        });

        // Replacing consonents + HAL
        sinhala_consonent_keys.forEach((con_char, idx) => {
            EN_pattern = con_char;
            SI_pattern = sinhala_consonant_map[con_char] + "්";
            RegEx_pattern = new RegExp(EN_pattern, "g");
            text = text.replace(RegEx_pattern, SI_pattern);
        });

        // Replacing vowels
        sinhala_vowels_keys.forEach((v_char, idx) => {
            EN_pattern = v_char;
            SI_pattern = sinhala_vowel_pure_map[v_char];
            RegEx_pattern = new RegExp(EN_pattern, "g");
            text = text.replace(RegEx_pattern, SI_pattern);
        });

        console.log(text);
        return (text);
    }

    var previous_input_text = "";
    var new_input_text = "";
    var outofscope_text = "";

    // TextBox Keys
    $(document).on('keypress', kbi_init_props["textMessageElement"], function (event) {
        switch_check = $('#flexSwitchCheckChecked').is(":checked");
        var key = (event.keyCode ? event.keyCode : event.which);

        if (switch_check) {

            if (key >= 20 && key <= 126) {
                previous_input_text += String.fromCharCode(key);
            }
            console.log("Accumilated: " + previous_input_text);
        }
    });

    // Handling Special Keys
    $(document).on('keydown', kbi_init_props["textMessageElement"], function (event) {
        // Only activates if the language is Sinhala
        switch_check = $('#flexSwitchCheckChecked').is(":checked");
        var key = (event.keyCode ? event.keyCode : event.which);

        // Handling the Backspace for Sinhalese
        if (switch_check) {
            if (key == 8) {

                var selection = window.getSelection();
                var selectedText = selection.toString();

                if (!selectedText) {
                    previous_input_text = "";
                    var current_val = $(kbi_init_props["textMessageElement"]).val();
                    current_val = current_val.substring(current_val.length - 1, -1);
                    outofscope_text = current_val;
                } else {
                    previous_input_text = "";
                    var current_val = $(kbi_init_props["textMessageElement"]).val();
                    var textComponent = document.getElementsByClassName('rw-new-message')[0];

                    var startPos = textComponent.selectionStart;
                    var endPos = textComponent.selectionEnd;
                    var selectedText = textComponent.value.substring(startPos, endPos);

                    // console.log(startPos, endPos, selectedText);
                    outofscope_text = current_val.substring(0, startPos) + current_val.substring(endPos,);
                }
            }
        }

        // Handling Enter (Submitting Text when Enter is pressed)
        if (key == 13) {
            $(kbi_init_props["sendMessageElement"]).trigger("click");
        }
        console.log(new_input_text);
    });

    // Filling the Text-box with the new value
    $(document).on('keyup', kbi_init_props["textMessageElement"], function (event) {
        // Only activates if the language is Sinhala
        switch_check = $('#flexSwitchCheckChecked').is(":checked");

        if (switch_check) {
            new_input_text = convert(previous_input_text);
            console.log(new_input_text);
            $(kbi_init_props["textMessageElement"]).val(outofscope_text + new_input_text);
        }
    });

    // Doc Keys
    // CTRL+Q Shortcut for switching languages
    var keys = {};

    $(document).keydown(function (event) {
        var key = (event.keyCode ? event.keyCode : event.which);

        if (key == 17) {
            if (81 in keys) {
                delete keys[81];
            }
        }
        if (key == 17 || key == 81) {
            keys[key] = true;
        } else {
            keys = {};
        }

        console.log(keys);
        switch_check = $('#flexSwitchCheckChecked').is(":checked");

        if (17 in keys && 81 in keys) {
            if (switch_check) {
                $("#flexSwitchCheckChecked").prop('checked', false);
                buildToast("", "Switched to English", "Press CTRL+Q to Switch back to Sinhala.", "", "media/lang_dark.png", "");
                $('.toast').toast('show');
                outofscope_text = "";
            } else {
                $("#flexSwitchCheckChecked").prop('checked', true);
                buildToast("", "Switched to Sinhala", "Press CTRL+Q to Switch back to English.", "", "media/lang_dark.png", "");
                $('.toast').toast('show');
                previous_input_text = "";
                outofscope_text = $(kbi_init_props["textMessageElement"]).val();
            }
        }
    });

    $(document).keyup(function (event) {
        var key = (event.keyCode ? event.keyCode : event.which);
        delete keys[key];
    });

    // For the switch
    $(document).on("click", ".rw-launcher", function (event) {
        if (
            JSON.parse(localStorage.getItem("chat_session"))["params"]["isChatOpen"]
        ) {
            $("#kbi_lang_switch").addClass("invisible");
            $("#kbi_lang_switch").removeClass("visible");
        } else {
            $("#kbi_lang_switch").addClass("visible");
            $("#kbi_lang_switch").removeClass("invisible");
        }

        if (kbi_init_props["disableSwitchAnimation"] === false) {
            event.preventDefault();
            $("#kbi_lang_switch").css({ right: "60px", left: "" }).animate({
                right: "89px",
            });
        }
    });

    $(window).bind("load", function () {
        if (
            JSON.parse(localStorage.getItem("chat_session"))["params"]["isChatOpen"]
        ) {
            $("#kbi_lang_switch").addClass("visible");
            $("#kbi_lang_switch").removeClass("invisible");
        } else {
            $("#kbi_lang_switch").addClass("invisible");
            $("#kbi_lang_switch").removeClass("visible");
        }
    });
});