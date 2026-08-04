# Protodifferences

| Item | Type |Rubicon | Optimizer | Decision | Notes |
|---|---|---|---|---| --- |
| package or Name of Enum or Message| package, enum, message, field, enum value| value in Rubicon| value in optimizer| Conflict, Same | 🟢 (Keep) 🔴 (Resolve) | 

## ConfigurationRequest


### Structure

| Item | Type |Rubicon | Optimizer | Decision | Notes |
|---|---|---|---|---| --- |
| package | package | ddd.config | ddd.config | Same | 🟢 |
| ConfigType | enum | same | same | Same values and numbering | 🟢 |
| ConfigurationItem | message | same | same | Same fields and values | 🟢 |

### Function

## Network Requests

The Rubicon Repo has more definitions that the student optimizer

### Structure


| Item | Type | Rubicon | Optimizer | Decision | Notes |
|---|---|---|---|---| --- |
| package | package | ddd.network | ddd.network | Same | 🟢 |
| import | import | UnitDefinition.proto | Missing | Conflict | Rubicon uses this package, further inspect |
| ActionType | enum | same | same | Same values and numbering | 🟢 |
| ConnectionType | enum | same | same | Same values and numbering | 🟢 |
| CallbackFunction | enum | CallbackFunction | Missing | Conflict | The Optimizer does not have this |
| CallbackFunction.FORWARD_CB | enum value | FORWARD_CB = 0 | Missing | Conflict | The Optimizer does not have this |
| CallbackFunction.QUERY_PLAN_CB | enum value | QUERY_PLAN_CB = 0 | Missing | Conflict | The Optimizer does not have this |
| ConnectionItem | message | same | same | Same values and Fileds | 🟢 |
| UuidForUnitResponse | message | same | same | Same values and fields | 🟢 |
| CallbackChangeRequest | message | CallbackChangeRequest | Missing | Conflict | 🔴 |
| CallbackChangeRequest.packageType | field | TcpPackageType packageType = 1 | Missing | Conflict | 🔴 |
| CallbackChangeRequest.packageType | field | CallbackFunction callbackFunction = 2 | Missing | Conflict | 🔴 |
| ServerConfigurationRequest | message | ServerConfigurationRequest | Missing | Conlict | 🔴 |
| ServerConfigurationRequest.callbackBackChange | field | CallBackChangeRequest callbackChange = 1 | Missing | Conlict | 🔴 |
| ServerConfigurationRequest.callbackBackChange | field | WindowSizeMS = 2 | Missing | Conlict | 🔴 |
| ServerConfigurationRequest.callbackBackChange | field | uint64 threshold = 3 | Missing | Conlict | 🔴 |
| ServerConfigurationRequest.callbackBackChange | field | float maxOverhead = 4 | Missing | Conlict | 🔴 |
| ServerConfigurationResponse | message | ServerConfigurationResponse | Missing | Conlict | 🔴 |
| ServerConfigurationRequest.success | field | bool success = 1 | Missing | Conlict | 🔴 |

## QueryPlan


### Structure

| Item | Type | Rubicon | Optimizer | Decision | Notes |
|---|---|---|---|---| --- |
| import | import | WorkItem.proto | Same | Same | 🟢 |
| QueryPlan | message | Same | Same | Same Values and Fields | 🟢 |
| Querygroup | message | QueryGroup | Missing | Conflict | 🔴 |
| Querygroup.groupID | field | uint64 groupID = 1 | Missing | Conflict | 🔴 |
| Querygroup.columnTransfers | field | WorkItem columnTransfers = 2 | Missing | Conflict | 🔴 |
| Querygroup.plans | field | QueryPlan plans = 3 | Missing | Conflict | 🔴 |

## TestAndBenchmark

Here both Rubicon and Optimizer are the same 

### Structure

| Item | Type | Rubicon | Optimizer | Decision | Notes |
|---|---|---|---|---| --- |
| pacakge | package | ddd.testing | ddd.testing | Same | 🟢 |
| BenchmarkAction | enum | BenchmarkAction | BenchmarkAction | Same Values and Numbering | 🟢 |
| DataType | enum | DataType | DataType | Same Values and Numbering | 🟢 |
| TestDataSetup | message | TestDataSetup | TestDataSetup | Same Values and Fields | 🟢 |

## UnitDefinition

TcpPackageType and UnitType are completely missing in the student optimizer

### Structure

| Item | Type | Rubicon | Optimizer | Decision | Notes |
|---|---|---|---|---| --- |
| TcpPackageType | enum | TcpPackageType | Missing | Conflict | 🔴 |
| UnitType | enum | UnitType | Missing | Conflict | 🔴 |
| UnitDefinition | message | UnitDefinition | Unitdefinition | Same Values and Fields | 🟢 |

## WorkItem //TODO

The Studentoptimizer contains an enum StringOperation, additional Values in the message FilterItem, aswell as more fields in JoinItem, additional fields in ResultItem. 


Rubicon contains the message DataTransferItem, which the optimizer is completely missing

DataTransferItem shows up the the message WorkItem in Rubicon. The field depens0n in DataTransferItem has different values for both Rubicon and Optimizer.
The Field returnExtendedResult in WorkItem exists in Rubicon and not in the Optimizer. 



### Structure

| Item | Type | Rubicon | Optimizer | Decision | Notes |
|---|---|---|---|---| --- |
|ColumnType|enum|ColumnType|ColumnType| Same Values and Numbers | 🟢 |
|CompType|enum|CompType|CompType| Same Values and Numbers | 🟢 |
|OperatorType|enum|OperatorType|OperatorType| Same Values and Numbers | 🟢 |
|StringOperation|enum| Missing |StringOperation|Conflict| 🔴 |
|StringOperation.STR_LOWER|enum value| Missing |StringOperation.STR_LOWER = 1|Conflict| 🔴 |
|StringOperation.STR_UPPER|enum value| Missing |StringOperation.STR_UPPER = 2|Conflict| 🔴 |
|AggFunc|enum| AggFunc |AggFunc|Same| 🟢 |
|RelOp|enum| AggFunc |AggFunc|Same| 🟢 |
|ArithOp|enum| AggFunc |AggFunc|Same| 🟢 |
|SIMDISE|enum| AggFunc |AggFunc|Same| 🟢 |
|IntValue|enum| AggFunc |AggFunc|Same| 🟢 |
|FloatValue|enum| AggFunc |AggFunc|Same| 🟢 |
|StringValue|enum| AggFunc |AggFunc|Same| 🟢 |
|ScalarValue|enum| AggFunc |AggFunc|Same| 🟢 |
|ColumnMessage|enum| AggFunc |AggFunc|Same| 🟢 |
|FilterItem|enum| AggFunc |AggFunc|Same| 🟢 |
|FilterItem.InputColumn|enum| AggFunc |AggFunc|Same| 🟢 |
|FilterItem.outputColumn|enum| AggFunc |AggFunc|Same| 🟢 |
|FilterItem.filterType|enum| AggFunc |AggFunc|Same| 🟢 |
|FilterItem.filterValue|enum| AggFunc |AggFunc|Same| 🟢 |
|FilterItem.stringOp|enum| AggFunc |AggFunc|Same| 🟢 |
|FilterItem.compareColumn|enum| AggFunc |AggFunc|Same| 🟢 |


|MultiGroupItem|enum| AggFunc |AggFunc|Same| 🟢 |
|JoinItem|enum| AggFunc |AggFunc|Same| 🟢 |

|JoinItem|enum| AggFunc |AggFunc|Same| 🟢 |
|JoinItem|enum| AggFunc |AggFunc|Same| 🟢 |
|AggItem|enum| AggFunc |AggFunc|Same| 🟢 |



## WorkRequest

### Structure

| Item | Type | Rubicon | Optimizer | Decision | Notes |
|---|---|---|---|---| --- |
|import|import| TestAndBenchmark.proto |Missing|Conflict| 🔴 |
|import|import| QueryPlan.proto |QueryPlan.proto|Same| 🟢 |
|import|import| WorkItem.proto |WorkItem.proto|Same| 🟢 |
|WorkRequest|message|WorkRequest|WorkRequest|Field Conflict| 🔴 |
|WorkRequest.reqeustItem|oneof|requestItem|RequestItem|Field Conflict| 🔴 |
|WorkRequest.requestItem.testDataSetup|field value|ddd.testing.TestDataSetup testDataSetup = 1 | string test = 1 |Field Conflict| 🔴 |
|WorkRequest.requestItem.queryPlan|field value|QueryPlan queryPlan = 2; | QueryPlan queryPlan = 2; | Same | 🟢 |
|WorkRequest.requestItem.workItem|field value|QueryPlan queryPlan = 2; | QueryPlan queryPlan = 2; | Same | 🟢 |
|WorkRequest.requestItem.testDataSetup|field value|WorkItem workItem = 3; | WorkItem workItem = 3; |Same| 🟢 |
|WorkRequest.requestItem.queryGroup|field value|QueryGroup queryGroup = 4; |Missing |Conflict| 🔴 |
|ForwardedWorkRequest|message|ForwardedWorkRequest | ForwardedWorkRequest |Same| 🟢 |


## WorkResponse

### Structure


| Item | Type | Rubicon | Optimizer | Decision | Notes |
|---|---|---|---|---| --- |
|WorkResponse|message|WorkResponse|WorkResponse|Same, but Field Mismatch| 🔴 |
|WorkResponse.planId|field|uint32 planId = 1|uint32 planId = 1|Same| 🟢 |
|WorkResponse.ItemId|field|uint32 ItemId = 2|uint32 ItemId = 2|Same| 🟢 |
|WorkResponse.info|field|string info = 3|string info = 3|Same| 🟢 |
|WorkResponse.success|field|bool success = 4|bool success = 4|Same| 🔴 |
|WorkResponse.ExetendedResult|field|ExtendedResult extendedresult = 5| Missing|Same| 🔴 |
|ExtendedResult|message|ExtendedResult| Missing |Conflict| 🔴 |
|PlanResposne|message|PlanResponse| Missing|Conflict| 🔴 |

