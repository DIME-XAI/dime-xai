import { Button, Stack } from "@mui/material";
import React, { Component } from "react";

export default class DeleteModal extends Component {
  render() {
    return (
      <div
        className="modal fade"
        id={this.props.id}
        tabIndex="-1"
        aria-hidden="true"
      >
        <div className="modal-dialog modal-dialog-centered">
          <div className="modal-content app-delete-modal app-delete-modal-model">
            <div className="modal-header" style={{ border: "none" }}>
              <h5 className="modal-title">{this.props.title}</h5>
              <button
                type="button"
                className="btn-close"
                data-bs-dismiss="modal"
                aria-label="Close"
              ></button>
            </div>
            <div className="modal-body" style={{ border: "none" }}>
              <p>{this.props.body}</p>
            </div>
            {this.props.buttonPrimary.button ||
            this.props.buttonSecondary.button ? (
              <div className="modal-footer" style={{ border: "none" }}>
                <Stack direction="row" spacing={1}>
                  {this.props.buttonSecondary.button && (
                    <Button
                      className={
                        "app-button " + this.props.buttonSecondary.buttonClass
                      }
                      variant={this.props.buttonSecondary.buttonVarient}
                      color={this.props.buttonSecondary.buttonType}
                      sx={{ border: "none", "&:hover": { border: "none" } }}
                      data-bs-dismiss="modal"
                    >
                      {this.props.buttonSecondary.buttonText}
                    </Button>
                  )}
                  {this.props.buttonPrimary.button && (
                    <Button
                      className={
                        "app-button " + this.props.buttonPrimary.buttonClass
                      }
                      variant={this.props.buttonPrimary.buttonVarient}
                      color={this.props.buttonPrimary.buttonType}
                      onClick={(e) =>
                        this.props.deleteHandler(e, this.props.item)
                      }
                      data-bs-dismiss="modal"
                      sx={{ border: "none", "&:hover": { border: "none" } }}
                    >
                      {this.props.buttonPrimary.buttonText}
                    </Button>
                  )}
                </Stack>
              </div>
            ) : (
              <></>
            )}
          </div>
        </div>
      </div>
    );
  }
}
