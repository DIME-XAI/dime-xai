import React from "react";

class ExplanationBar extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      sliderValue: this.props.sliderValue ? this.props.sliderValue : "0%",
      sliderColorPrimary: this.props.sliderColorPrimary
        ? this.props.sliderColorPrimary
        : `material-progress-slider-primary-${this.props.color}`,
      sliderColorSecondary: this.props.sliderColorSecondary
        ? this.props.sliderColorSecondary
        : `material-progress-slider-secondary-${this.props.color}`,
      progressBarColor: this.props.progressBarColor
        ? this.props.progressBarColor
        : `material-progress-slider-background-${this.props.color}`,
      labelColor: this.props.labelColor
        ? this.props.labelColor
        : "material-progress-label-f",
      token: this.props.token ? this.props.token : "Unknown",
    };

    this.moveSlider = this.moveSlider.bind(this);
  }

  moveSlider(event) {
    console.log("moveSlider was called");
  }

  render() {
    return (
      <div className="d-flex mb-3">
        <div className="col-3 col-lg-3 col-sm-2 text-center">
          <p
            className={`my-auto text-end h6 app-progress-label ${this.state.labelColor}`}
          >
            {this.state.token}
          </p>
          <p
            className={`my-auto text-end h6 app-progress-label ${this.state.labelColor}`}
          >
            {this.state.sliderValue}
          </p>
        </div>
        <div className="col-9 col-lg-9 col-sm-10 ps-2">
          <div
            className={`overflow-hidden container-middle container-bg-custom w-100 align-middle m-0 app-progress-bar ${this.state.progressBarColor}`}
          >
            <div
              className={`shadow container-middle container-bg-custom align-middle m-0 app-progress-slider d-flex ${this.state.sliderColorPrimary}`}
              style={{ width: this.state.sliderValue }}
            >
              <div
                className={`w-100 h-25 material-dark-blue mt-auto ${this.state.sliderColorSecondary}`}
                style={{
                  borderBottomLeftRadius: "50px",
                  borderBottomRightRadius: "50px",
                }}
              ></div>
            </div>
          </div>
        </div>
      </div>
    );
  }
}

export default ExplanationBar;
