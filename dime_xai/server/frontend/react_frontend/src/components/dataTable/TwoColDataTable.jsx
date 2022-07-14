import React, { Component } from 'react';

export default class TwoColDataTable extends Component {
  render() {
    let tableData = Object.keys(this.props.data).map((key, index) =>
      <tr key={key}>
        <td>{key}</td>
        <td>{this.props.data[key]}</td>
      </tr>
    );
    return (
      <table className={`table table-sm app-table ${this.props.classNames}`}>
        <tbody>
          {tableData}
        </tbody>
      </table>
    );
  }
}
