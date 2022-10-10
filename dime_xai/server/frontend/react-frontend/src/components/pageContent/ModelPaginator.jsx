import * as React from "react";
import Pagination from "@mui/material/Pagination";
import { Box } from "@mui/system";
import ModelListItem from "./ModelListItem";

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
    data: paginatedItems,
  };
}

const ModelPaginator = (props) => {
  const [page, setPage] = React.useState(1);
  const handleChange = (event, value) => {
    setPage(paginator(props.modelList, value, 1).page);
  };

  return (
    <>
      {props.modelList.length > 0 ? (
        <>
          {paginator(props.modelList, page, props.perPageItems).data.map(
            (model, index) => {
              return (
                <ModelListItem
                  key={props.generateModalId(model.name)}
                  modelName={model.name}
                  modelSize={model.size}
                  modelId={props.generateModalId(model.name)}
                  compatibilityChip={false}
                  handleDelete={props.handleDelete}
                />
              );
            }
          )}
          <Box
            style={{ display: "flex", justifyContent: "center" }}
            sx={{ marginY: "20px" }}
          >
            <Pagination
              className="app-paginator"
              count={
                paginator(props.modelList, page, props.perPageItems).total_pages
              }
              page={paginator(props.modelList, page, props.perPageItems).page}
              onChange={handleChange}
              variant="contained"
            />
          </Box>
        </>
      ) : (
        <Box className="p-3">
          Currently there are no Trained Models Available
        </Box>
      )}
    </>
  );
};

export default ModelPaginator;
