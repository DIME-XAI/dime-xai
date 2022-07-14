let api = "http://localhost:6066"; 
//"http://localhost:6066";

let dimeDocsHost = "https://dime-xai.github.io";
// https://kolloqe.github.io/

export const configs = {
  api: api,
  explainEndpoint: `${api}/api/dime/explain`,
  abortExplainEndpoint: `${api}/api/dime/abort`,
  statsEndpoint: `${api}/api/dime/stats`,
  modelEndpoint: `${api}/api/dime/model`,
  explanationEndpoint: `${api}/api/dime/explanation`,
  visualizationEndpoint: `${api}/api/dime/explanation/visualize`,
  configEndpoint: `${api}/api/dime/configs`,
  dimeDocsHost: `${dimeDocsHost}`,
  dimeDocsDocs: `${dimeDocsHost}/docs`,
  dimeDocsMatrix: `${dimeDocsHost}/compatibility-matrix`,
  dimeDocsDIET: `${dimeDocsHost}/custom-diet`,
  dimeConfigs: `${dimeDocsHost}/dime-configs`,
  dimeVersion: `1.0.0`,
  dimeGitHub: `https://www.github.com/dime-xai`,
  snackbarVerticalPosition: "bottom",
  snackbarHorizontalPostion: "left",
};

export const dime_ascii = `

                  .:*%%*:.                        
                  |@@@@@@@@@@@#:.                 
           .:|    |@@@#:'':#@@@@@@@#:.            
         |@@@|    |@@@|    |@@@@@@@@@@@#:.        
         |@@@|    |:'      |@@@| ':#@@@@@@@#:.    
         |@@@|             |@@@|   ':@@@@@@@@@@#:.
    .:#@@@@@@|      .:|    |@@@|    |@@@| ':#@@@@|
.:#@@@@@@@@@@|    |@@@|    |@@@|    |@@@|   ':@@@|
|@@@@#:' |@@@|    |@@@|    |@@@|    |@@@|    |@@@|
|@@@|    |@@@|    |@@@|    |@@@|    |@@@|    |@@@|
|@@@|    |@@@|    |@@@|    |@@@|    |@@@|    |@@@|
|@@@|    |@@@|    |@@@|    |@@@|    |@@@|    |@@@|
|@@@|    |@@@|    |@@@|    |@@@|    |@@@|    |@@@|
|@@@|    |@@@|    |@@@|                           
|@@@|    |@@@|    |@@@|    |@@@@@@@@@@@@@@@@@@@@@|
|@@@|    |@@@|    |@@@|    |@@@@@@@@@@@@@@@@@@@@@|
|@@@|    |@@@|    |@@@|    |@@@|           .:@@@@|
|@@@|    |@@@|    |@@@|    |@@@|      .:+#@@@@@@@|
|@@@|    |@@@|    |@@@|    |@@@|.:+#@@@@@@@@#:'   
|@@@|    |@@@|    |@@@|    |@@@@@@@@@@@#:'      .|
|@@@#:.  |@@@|    |@@@|    |@@@@@@#+:'     .:#@@@|
|@@@@@@:.|@@@|    |@@@|    |@@@|      .:#@@@@@@@@|
  ':@@@@@@@@@|    |@@@|    |@@@|  .:#@@@@@@@#:'   
      ':@@@@@|    |@@@|    |@@@|#@@@@@@@#:'       
          ':@|    |@@@#:..:#@@@@@@@@#:'           
                  |@@@@@@@@@@@@@#:'           XAI 
                    ':#%@@%#:'                    

`;

export const dime_ascii_sm = `
       .:%@@@@@@@@%:.  
     .:|  |@:'':@@@@@@:.   
     |@|  |:'  |@|'':@@@@@:.
.:@@@@@|       |@|  |@|'':@|
|@:''|@|  .:|  |@|  |@|  |@|
|@|  |@|  |@|  |@|  |@|  |@|
|@|  |@|  |@|  
|@|  |@|  |@|  |@@@@@@@@@@@|
|@|  |@|  |@|  |@|       |@|
|@:..|@|  |@|  |@@@@@@@@@@:'
':@@@@@|  |@|  |@|     
   ':@@|  |@:..:@@@@@@:'   
       ':%@@@@@@@@%:'
`;


// https://dev.to/rajeshroyal/reactjs-disable-consolelog-in-production-and-staging-3l38
export const GlobalDebug = (function () {
  var savedConsole = console;
  /**
  * @param {boolean} debugOn
  * @param {boolean} suppressAll
  */
  return function (debugOn, suppressAll) {
    var suppress = suppressAll || false;
    if (debugOn === false) {
      // supress the default console functionality
      // eslint-disable-next-line
      console = {};
      console.log = function () { };
      // supress all type of consoles
      if (suppress) {
        console.info = function () { };
        console.warn = function () { };
        console.error = function () { };
      } else {
        console.info = savedConsole.info;
        console.warn = savedConsole.warn;
        console.error = savedConsole.error;
      }
    } else {
      // eslint-disable-next-line
      console = savedConsole;
    }
  };
})();
