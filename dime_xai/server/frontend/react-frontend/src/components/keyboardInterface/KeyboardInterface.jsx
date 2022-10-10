import { Input, TextField } from "@mui/material";
import React, { Component } from "react";
import PropTypes, { number, string } from "prop-types";

export default class KeyboardInput extends Component {
  constructor(props) {
    super(props);
    this.state = {
      language: this.props?.defaultLanguage,
      text: this.props?.value || "",
      previousText: "",
      newText: "",
      outOfScopeText: this.props?.value || "",
      shortcutKeyStore: {},
    };

    // refs
    const utilizeFocus = () => {
      const ref = React.createRef();
      const setFocus = () => {
        ref.current && ref.current.focus();
      };
      return { setFocus, ref };
    };
    this.inputRef = utilizeFocus();

    // handlers
    this.handleInputChange = this.handleInputChange.bind(this);
    this.handleInputKeyDown = this.handleInputKeyDown.bind(this);
    this.handleInputKeyUp = this.handleInputKeyUp.bind(this);
    this.handleInputKeyPress = this.handleInputKeyPress.bind(this);
    this.handleInputReset = this.handleInputReset.bind(this);
    this.handleInputFocus = this.handleInputFocus.bind(this);
    this.handleConvert = this.handleConvert.bind(this);
    this.handleLanguage = this.handleLanguage.bind(this);
    this.setText = this.setText.bind(this);
  }

  componentDidMount() {
    this.handleInputFocus();

    if (!(this.state.language === "si" || this.state.language === "en")) {
      this.setState({
        language: "si",
      });

      if (this.props.handleShortcut) {
        this.props.handleShortcut("si");
      }
    } else if (this.state.language === "si") {
      if (this.props.handleShortcut) {
        this.props.handleShortcut("si");
      }
    } else {
      if (this.props.handleShortcut) {
        this.props.handleShortcut("en");
      }
    }
  }

  // keyboard functions
  handleInputKeyPress(event) {
    let keyCode = event.keyCode ? event.keyCode : event.which;
    if (this.state.language === "si") {
      if (
        keyCode >= 32 &&
        keyCode <= 126 &&
        [37, 38, 39, 40].indexOf(keyCode) === -1
      ) {
        this.setState(
          {
            previousText:
              this.state.previousText + String.fromCharCode(keyCode),
          }
          // // callback has been disabled for boosting performance. re-enable to debug if required
          // () => {
          //   console.log("Accumilated: " + this.state.previousText);
          // }
        );
      }
    }
  }

  handleInputKeyDown(event, enterKeyHandler, shortcutKeyHandler) {
    let keyCode = event.keyCode ? event.keyCode : event.which;

    // Handling the Backspace for Sinhalese
    if (this.state.language === "si") {
      let selection = window.getSelection();
      let selectedText = selection.toString();

      if (keyCode === 8) {
        if (!selectedText) {
          this.setState({
            previousText: "",
          });
          let currentValue = this.state.text;
          currentValue = currentValue.substring(currentValue.length - 1, -1);
          this.setState({
            outOfScopeText: currentValue,
          });
        } else {
          this.setState({
            previousText: "",
          });
          const currentValue = this.state.text;
          const startPos = this.inputRef.ref.current.selectionStart;
          const endPos = this.inputRef.ref.current.selectionEnd;
          // const selectedText = currentValue.substring(startPos, endPos);

          this.setState({
            outOfScopeText:
              currentValue.substring(0, startPos) +
              currentValue.substring(endPos),
          });
        }
      } else if (
        keyCode >= 32 &&
        keyCode <= 126 &&
        [37, 38, 39, 40].indexOf(keyCode) === -1
      ) {
        if (selectedText) {
          this.setState({
            previousText: "",
          });
          const currentValue = this.state.text;
          const startPos = this.inputRef.ref.current.selectionStart;
          const endPos = this.inputRef.ref.current.selectionEnd;
          // const selectedText = currentValue.substring(startPos, endPos);
          this.inputRef.ref.current.setSelectionRange(
            currentValue.length,
            startPos
          );

          this.setState({
            outOfScopeText:
              currentValue.substring(0, startPos) +
              currentValue.substring(endPos),
          });
        }
      }
    }

    // trigger enter if handler available
    if (keyCode === 13) {
      if (enterKeyHandler !== null && enterKeyHandler !== undefined) {
        enterKeyHandler();
        this.handleInputReset();
      }
    }

    // trigger shortcut
    if (this.props.enableShortcuts) {
      if (keyCode === 17) {
        let shortcutKeyStore = this.state.shortcutKeyStore;
        if (Number(this.props.shortcutKey) in shortcutKeyStore) {
          delete shortcutKeyStore[Number(this.props.shortcutKey)];
          this.setState({
            shortcutKeyStore,
          });
        }
      }
      if (keyCode === 17 || keyCode === Number(this.props.shortcutKey)) {
        let shortcutKeyStore = this.state.shortcutKeyStore;
        shortcutKeyStore[keyCode] = true;
        this.setState({
          shortcutKeyStore,
        });
      } else {
        this.setState({
          shortcutKeyStore: {},
        });
      }
    }

    if (
      17 in this.state.shortcutKeyStore &&
      Number(this.props.shortcutKey) in this.state.shortcutKeyStore
    ) {
      if (shortcutKeyHandler !== null && shortcutKeyHandler !== undefined) {
        if (this.state.language === "si") {
          shortcutKeyHandler("en");
        } else {
          shortcutKeyHandler("si");
        }
      } else {
        if (this.state.language === "si") {
          this.setState({
            outOfScopeText: "",
            language: "en",
          });
        } else {
          this.setState({
            previousText: "",
            outOfScopeText: this.state.text,
            language: "si",
          });
        }
      }
    }
  }

  handleInputKeyUp(event) {
    var keyCode = event.keyCode ? event.keyCode : event.which;
    let shortcutKeyStore = this.state.shortcutKeyStore;
    delete shortcutKeyStore[keyCode];
    this.setState({
      shortcutKeyStore: shortcutKeyStore,
    });

    // Only activates if the language is Sinhala
    if (this.state.language === "si") {
      this.setState(
        {
          newText: this.handleConvert(this.state.previousText),
        },
        () => {
          this.setState(
            {
              text: this.state.outOfScopeText + this.state.newText,
            },
            () => {
              if (
                this.props.handleTextChange !== null &&
                this.props.handleTextChange !== undefined
              ) {
                this.props.handleTextChange(this.state.text);
              }
            }
          );
        }
      );
    }
  }

  handleConvert(text) {
    // Vowel Keys and Maps
    let sinhala_vowels_keys = [
      "uu",
      "oo",
      "oe",
      "aa",
      "AA",
      "Aa",
      "ae",
      "ii",
      "ie",
      "ee",
      "ea",
      "ei",
      "uu",
      "au",
      "O",
      "a",
      "A",
      "i",
      "e",
      "u",
      "U",
      "o",
      "E",
      "I",
    ];
    let sinhala_vowel_pure_map = {
      uu: "ඌ",
      oo: "ඕ",
      oe: "ඕ",
      aa: "ආ",
      AA: "ඈ",
      Aa: "ඈ",
      ae: "ඈ",
      ii: "ඊ",
      ie: "ඊ",
      ee: "ඒ",
      ea: "ඒ",
      ei: "ඒ",
      au: "ඖ",
      O: "ඖ",
      a: "අ",
      A: "ඇ",
      i: "ඉ",
      e: "එ",
      u: "උ",
      U: "උ",
      o: "ඔ",
      E: "ඓ",
      I: "ඓ",
    };
    let sinhala_vowel_suffix_map = {
      uu: "ූ",
      oo: "ෝ",
      oe: "ෝ",
      aa: "ා",
      AA: "ෑ",
      Aa: "ෑ",
      ae: "ෑ",
      ii: "ී",
      ie: "ී",
      ee: "ේ",
      ea: "ේ",
      ei: "ේ",
      au: "ෞ",
      O: "ෞ",
      a: "",
      A: "ැ",
      i: "ි",
      e: "ෙ",
      u: "ු",
      o: "ො",
      E: "ෛ",
      I: "ෛ",
    };

    // Non-joining Character Keys and Maps [ + '\u200D']
    let sinhala_nonjoining_keys = ["RR", "z", "x", "H", "R"];
    let sinhala_nonjoining_map = {
      RR: "ඎ",
      z: "ර්\u200D",
      x: "ං",
      H: "ඃ",
      R: "ඍ",
    };

    // Consonent Keys and Maps
    let sinhala_consonent_keys = [
      "nndh",
      "nnd",
      "nng",
      "mmb",
      "GN",
      "KN",
      "Lu",
      "Th",
      "Dh",
      "gh",
      "Ch",
      "ph",
      "kh",
      "bh",
      "Sh",
      "sh",
      "dh",
      "ch",
      "th",
      "N",
      "L",
      "K",
      "G",
      "T",
      "D",
      "P",
      "B",
      "C",
      "X",
      "J",
      "t",
      "k",
      "d",
      "n",
      "p",
      "b",
      "m",
      "M",
      "Y",
      "y",
      "j",
      "l",
      "v",
      "w",
      "V",
      "W",
      "s",
      "S",
      "h",
      "f",
      "F",
      "g",
      "c",
      "r",
    ];
    let sinhala_consonant_map = {
      nndh: "ඳ",
      nnd: "ඬ",
      nng: "ඟ",
      mmb: "ඹ",
      GN: "ඥ",
      KN: "ඤ",
      Lu: "ළු",
      Th: "ථ",
      Dh: "ධ",
      gh: "ඝ",
      Ch: "ඡ",
      ph: "ඵ",
      kh: "ඛ",
      bh: "භ",
      Sh: "ෂ",
      sh: "ශ",
      dh: "ද",
      ch: "ච",
      th: "ත",
      N: "ණ",
      L: "ළ",
      K: "ඛ",
      G: "ඝ",
      T: "ඨ",
      D: "ඪ",
      P: "ඵ",
      B: "භ",
      C: "ඡ",
      X: "ඞ",
      J: "ඣ",
      t: "ට",
      k: "ක",
      d: "ඩ",
      n: "න",
      p: "ප",
      b: "බ",
      m: "ම",
      M: "ම",
      Y: "ය",
      y: "ය",
      j: "ජ",
      l: "ල",
      v: "ව",
      w: "ව",
      V: "ව",
      W: "ව",
      s: "ස",
      S: "ස",
      h: "හ",
      f: "ෆ",
      F: "ෆ",
      g: "ග",
      c: "ච",
      r: "ර",
    };
    // consonantsUni[14] = 'ළු' is handled automatically through Unicode

    // Special Character Keys and Maps
    let sinhala_special_keys = ["ruu", "ru"];
    let sinhala_special_map = {
      ruu: "ෲ",
      ru: "ෘ",
    };

    let EN_pattern, SI_pattern, RegEx_pattern;

    // Replacing non-joining characters
    sinhala_nonjoining_keys.forEach((nj_char) => {
      EN_pattern = nj_char;
      SI_pattern = sinhala_nonjoining_map[nj_char];
      RegEx_pattern = new RegExp(EN_pattern, "g");
      text = text.replace(RegEx_pattern, SI_pattern);
    });

    // Replacing special consonents
    sinhala_special_keys.forEach((sp_char) => {
      sinhala_consonent_keys.forEach((con_char) => {
        EN_pattern = con_char + sp_char;
        SI_pattern =
          sinhala_consonant_map[con_char] + sinhala_special_map[sp_char];
        RegEx_pattern = new RegExp(EN_pattern, "g");
        text = text.replace(RegEx_pattern, SI_pattern);
      });
    });

    // Replacing consonants + Rakaransha + vowel modifiers
    sinhala_consonent_keys.forEach((con_char) => {
      sinhala_vowels_keys.forEach((v_char) => {
        EN_pattern = con_char + "r" + v_char;
        SI_pattern =
          sinhala_consonant_map[con_char] +
          "්‍ර" +
          sinhala_vowel_suffix_map[v_char];
        RegEx_pattern = new RegExp(EN_pattern, "g");
        text = text.replace(RegEx_pattern, SI_pattern);
      });
      EN_pattern = con_char + "r";
      SI_pattern = sinhala_consonant_map[con_char] + "්‍ර";
      RegEx_pattern = new RegExp(EN_pattern, "g");
      text = text.replace(RegEx_pattern, SI_pattern);
    });

    // Replacing consonents + vowel modifiers
    sinhala_consonent_keys.forEach((con_char) => {
      sinhala_vowels_keys.forEach((v_char) => {
        EN_pattern = con_char + v_char;
        SI_pattern =
          sinhala_consonant_map[con_char] + sinhala_vowel_suffix_map[v_char];
        RegEx_pattern = new RegExp(EN_pattern, "g");
        text = text.replace(RegEx_pattern, SI_pattern);
      });
    });

    // Replacing consonents + HAL
    sinhala_consonent_keys.forEach((con_char) => {
      EN_pattern = con_char;
      SI_pattern = sinhala_consonant_map[con_char] + "්";
      RegEx_pattern = new RegExp(EN_pattern, "g");
      text = text.replace(RegEx_pattern, SI_pattern);
    });

    // Replacing vowels
    sinhala_vowels_keys.forEach((v_char) => {
      EN_pattern = v_char;
      SI_pattern = sinhala_vowel_pure_map[v_char];
      RegEx_pattern = new RegExp(EN_pattern, "g");
      text = text.replace(RegEx_pattern, SI_pattern);
    });

    return text;
  }

  // component functions
  handleLanguage(language) {
    if (language === "en") {
      this.setState({
        outOfScopeText: "",
        language: "en",
      });
    } else {
      this.setState({
        previousText: "",
        outOfScopeText: this.state.text,
        language: "si",
      });
    }
  }

  setText(text) {
    this.setState({
      text: text,
      previousText: "",
      newText: "",
      outOfScopeText: text,
    });
  }

  resetText() {
    this.setState({
      text: "",
      previousText: "",
      newText: "",
      outOfScopeText: "",
    });
  }

  getText() {
    return this.state.text;
  }

  handleInputChange(event, inputChangeHandler) {
    this.setState(
      {
        text: event.target.value,
      },
      () => {
        if (inputChangeHandler !== null && inputChangeHandler !== undefined) {
          inputChangeHandler(event);
        }
      }
    );
  }

  handleInputReset() {
    this.setState({
      text: "",
      previousText: "",
      newText: "",
      outOfScopeText: "",
    });
  }

  handleInputFocus() {
    this.inputRef.setFocus();
  }

  render() {
    return this.props.interface === "textfield" ? (
      <TextField
        id={this.props.id}
        name={this.props.name}
        type={this.props.type}
        inputProps={this.props.inputProps}
        margin={this.props.margin}
        className={" " + this.props.className}
        hiddenLabel={this.props.hiddenLabel}
        label={this.props.label}
        size={this.props.size}
        variant={this.props.variant}
        autoFocus={this.props.autoFocus}
        inputRef={this.inputRef.ref}
        error={this.props.error}
        helperText={this.props.helperText}
        value={this.state.text}
        defaultValue={this.props.defaultValue}
        placeholder={this.props.placeholder}
        onChange={(e) => {
          this.handleInputChange(e, this.props?.handleChange || null);
        }}
        onKeyDown={(e) => {
          this.handleInputKeyDown(
            e,
            this.props?.handleEnter || null,
            this.props?.handleShortcut || null
          );
        }}
        onKeyUp={(e) => {
          this.handleInputKeyUp(e);
        }}
        onKeyPress={(e) => {
          this.handleInputKeyPress(e);
        }}
        disabled={this.props.disabled}
        required={this.props.required}
        fullWidth={this.props.fullWidth}
      />
    ) : (
      <Input
        id={this.props.id}
        name={this.props.name}
        type={this.props.type}
        inputProps={this.props.inputProps}
        margin={this.props.margin}
        placeholder={this.props?.placeholder || "Type a message here..."}
        className={" " + this.props.className}
        color={this.props.color || "secondary"}
        size={this.props.size}
        disableUnderline={this.props.disableUnderline || false}
        inputRef={this.inputRef.ref}
        error={this.props.error}
        autoFocus={this.props.autoFocus}
        value={this.state.text}
        defaultValue={this.props.defaultValue}
        onChange={(e) => {
          this.handleInputChange(e, this.props?.handleChange || null);
        }}
        onKeyDown={(e) => {
          this.handleInputKeyDown(
            e,
            this.props?.handleEnter || null,
            this.props?.handleShortcut || null
          );
        }}
        onKeyUp={(e) => {
          this.handleInputKeyUp(e);
        }}
        onKeyPress={(e) => {
          this.handleInputKeyPress(e);
        }}
        disabled={this.props.disabled}
        required={this.props.required}
        fullWidth={this.props.fullWidth}
      />
    );
  }
}

KeyboardInput.propTypes = {
  id: PropTypes.string,
  name: PropTypes.string,
  type: PropTypes.string,
  variant: PropTypes.oneOf(["filled", "outlined", "standard"]),
  inputProps: PropTypes.object,
  required: PropTypes.bool,
  margin: PropTypes.oneOf(["none", "dense", "normal"]),
  interface: PropTypes.oneOf(["input", "textfield"]).isRequired,
  value: PropTypes.string,
  defaultValue: PropTypes.any,
  placeholder: PropTypes.string,
  className: PropTypes.string,
  autoFocus: PropTypes.bool,
  size: PropTypes.oneOf(["small", "medium"]),
  color: PropTypes.oneOf(["primary", "secondary", string]),
  label: PropTypes.node,
  hiddenLabel: PropTypes.bool,
  disableUnderline: PropTypes.bool,
  defaultLanguage: PropTypes.oneOf(["en", "si"]),
  handleChange: PropTypes.func,
  handleTextChange: PropTypes.func,
  handleShortcut: PropTypes.func,
  handleEnter: PropTypes.func,
  enableShortcuts: PropTypes.bool,
  shortcutKey: PropTypes.oneOf([32, 81, number]),
  error: PropTypes.bool,
  helperText: PropTypes.string,
  disabled: PropTypes.bool,
  fullWidth: PropTypes.bool,
};

KeyboardInput.defaultProps = {
  id: undefined,
  name: undefined,
  type: undefined,
  variant: "filled",
  inputProps: {},
  margin: "none",
  required: false,
  interface: "input",
  value: "",
  defaultValue: undefined,
  placeholder: "Type here...",
  className: "w-100",
  autoFocus: true,
  size: "small",
  color: "primary",
  label: undefined,
  hiddenLabel: true,
  disableUnderline: true,
  defaultLanguage: "en",
  handleChange: undefined,
  handleTextChange: undefined,
  handleShortcut: undefined,
  handleEnter: undefined,
  enableShortcuts: true,
  shortcutKey: 81,
  error: false,
  helperText: "",
  disabled: false,
  fullWidth: false,
};
