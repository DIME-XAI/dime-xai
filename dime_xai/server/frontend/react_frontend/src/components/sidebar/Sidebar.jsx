import React from 'react';
import { Link } from 'react-router-dom';
import dimeGray from './dimeGray.png';
import VersionModal from '../modal/VersionModal';

class Sidebar extends React.Component {
  constructor(props) {
    super(props);
    this.handleTheme = this.handleTheme.bind(this);
  }

  handleTheme(event) {
    this.props.handleAppTheme();
  }

  render() {
    return (
      <>
        <div id="mySidebar" className="sidebar sidebar-dark">
          <div className="container sidebar-logo-container">
            <div className="row">
              <div className="span4"></div>
              <div className="span4 text-center">
                <img
                  className="center-block sidebar-logo"
                  src={dimeGray}
                  alt=""
                  role={"button"}
                  data-bs-toggle="modal"
                  data-bs-target={`#dime-version-modal`}
                />
              </div>
              <div className="span4"></div>
            </div>
          </div>
          <div
            className={`app-sidebar-link ${this.props.activeLink === "dashboard" && "app-sidebar-link-active"}`}
          // onClick={(e) => { this.props.setActiveLink(e, "dashboard") }}
          >
            <Link
              to="/"
              className={`sidebar-link ripple-button`}
              id="sidebar-dash">
              <span className="material-icons material-sidebar-icon">
                code
              </span>
              <span className="icon-text">
                Dashboard
              </span>
            </Link>
          </div>
          <br />
          <div className={`app-sidebar-link ${this.props.activeLink === "models" && "app-sidebar-link-active"}`}
          // onClick={(e) => { this.props.setActiveLink(e, "models") }}
          >
            <Link to="/models" className="sidebar-link ripple-button" id="sidebar-models">
              <span className="material-icons material-sidebar-icon">
                view_in_ar
              </span>
              <span className="icon-text">
                Models
              </span>
            </Link>
          </div>
          <br />
          <div className={`app-sidebar-link ${this.props.activeLink === "explanations" && "app-sidebar-link-active"}`}
          // onClick={(e) => { this.props.setActiveLink(e, "explanations") }}
          >
            <Link to="/explanations" className="sidebar-link ripple-button" id="sidebar-explanations">
              <span className="material-icons material-sidebar-icon">
                psychology_alt
              </span>
              <span className="icon-text">
                Explanations
              </span>
            </Link>
          </div>
          <br />
          <div className="app-sidebar-link">
            <label htmlFor="dark-mode-switch" className="sidebar-link ripple-button" id="sidebar-dark-mode" onClick={this.handleTheme}>
              <span className="material-icons material-sidebar-icon" id="sidebar-dark-mode-icon">
                dark_mode
              </span>
              <span className="icon-text">
                Dark Mode
              </span>
            </label>
          </div>
        </div>
        <VersionModal />
      </>
    );
  }
}

export default Sidebar