import * as React from "react";
import Pagination from "@mui/material/Pagination";
import ExplanationListItem from "./ExplanationListItem";
import { Box } from "@mui/system";

// https://codesandbox.io/s/tekvwr?file=/demo.js:4400-4699
function paginator(items, current_page, per_page_items) {
  let page = current_page || 1,
    per_page = per_page_items || 2,
    offset = (page - 1) * per_page,
    paginatedItems = items.slice(offset).slice(0, per_page_items),
    total_pages = Math.ceil(items.length / per_page);
  // console.log(total_pages, items.length, per_page);

  return {
    page: page,
    per_page: per_page,
    pre_page: page - 1 ? page - 1 : null,
    next_page: total_pages > page ? page + 1 : null,
    total: items.length,
    total_pages: total_pages,
    data: paginatedItems
  };
}

const ExplanationPaginator = (props) => {
  const [page, setPage] = React.useState(1);
  const handleChange = (event, value) => {
    setPage(paginator(props.explanationList, value, 1).page);
  };

  return (
    <>
      {props.explanationList.length > 0 ?
        <>
          {paginator(props.explanationList, page, props.perPageItems).data.map((explanation, index) => {
            return (
              <ExplanationListItem
                key={props.generateModalId(explanation)}
                explanationName={explanation}
                explanationId={props.generateModalId(explanation)}
                explanationDate={props.generateExplanationDate(explanation)}
                handleDelete={props.handleDelete}
                handleDownload={props.handleDownload}
                handleVisualize={props.handleVisualize}
                originChip={props.originChip} />
            );
          })}
          <Box
            style={{ display: "flex", justifyContent: "center" }}
            sx={{ marginY: "20px" }}>
            <Pagination
              className="app-paginator"
              count={paginator(props.explanationList, page, props.perPageItems).total_pages}
              page={paginator(props.explanationList, page, props.perPageItems).page}
              onChange={handleChange}
              variant="contained"
            />
          </Box>
        </>
        :
        <Box className='p-3'>
          Currently there are no Explanations Available
        </Box>
      }
    </>
  );
}

export default ExplanationPaginator;
