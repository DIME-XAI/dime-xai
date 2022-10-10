import React, { Component } from "react";
import { Box, Button } from "@mui/material";
import { Link } from "react-router-dom";

export default class AppTile extends Component {
  render() {
    return (
      <Box
        className={"col p-0 m-0 d-inline-block " + this.props.spacing}
        height={"100"}
      >
        <Box
          className={
            "p-4 m-0 shadow container-middle container-bg-custom w-100 " +
            this.props.bgcolor
          }
          height={"100%"}
        >
          <Box className="icon-square d-inline-flex align-items-center justify-content-center fs-4 flex-shrink-0 me-3">
            <span
              className={
                "material-icons material-feature-icon " + this.props.iconColor
              }
            >
              {this.props.icon}
            </span>
          </Box>
          <Box>
            <h4>
              <span className="display-6">{this.props.count}</span>
              {this.props.title}
            </h4>
            <p>{this.props.content}</p>
            {this.props.button.button &&
              (this.props.button.externalLink ? (
                <a
                  href={this.props.button.link}
                  target="_blank"
                  className="app-button"
                  rel="noreferrer"
                >
                  <Button
                    className={"app-button " + this.props.button.buttonType}
                    variant="outlined"
                    sx={{ border: "none", "&:hover": { border: "none" } }}
                  >
                    {this.props.button.buttonText}
                  </Button>
                </a>
              ) : (
                <Link to={this.props.button.link} className="app-button">
                  <Button
                    className={"app-button " + this.props.button.buttonType}
                    variant="outlined"
                    sx={{ border: "none", "&:hover": { border: "none" } }}
                  >
                    {this.props.button.buttonText}
                  </Button>
                </Link>
              ))}
            {this.props.customButton !== "" ? (
              <Button
                className={"app-button " + this.props.customButton.buttonType}
                variant="outlined"
                sx={{
                  border: "none",
                  "&:hover": { border: "none" },
                }}
                onClick={this.props.customButton.onClickHandler}
              >
                {this.props.customButton.buttonText}
              </Button>
            ) : (
              <></>
            )}
          </Box>
        </Box>
      </Box>
    );
  }
}
