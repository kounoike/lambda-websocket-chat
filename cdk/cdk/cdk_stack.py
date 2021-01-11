from aws_cdk import core
import aws_cdk.aws_dynamodb as dynamodb
import aws_cdk.aws_apigatewayv2 as apigwv2
from aws_cdk.aws_lambda_python import PythonFunction
import aws_cdk.aws_iam as iam


class CdkStack(core.Stack):
    def __init__(self, scope: core.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here
        ddb_table = dynamodb.Table(
            self,
            "WebSocketConnection",
            partition_key=dynamodb.Attribute(
                name="connectionId", type=dynamodb.AttributeType.STRING
            ),
            table_name="WebSocketConnection",
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=core.RemovalPolicy.DESTROY,
        )
        api = apigwv2.CfnApi(
            self,
            "WebSocketApi",
            name="WebSocketApi",
            protocol_type="WEBSOCKET",
            route_selection_expression="$request.body.action",
        )

        connect_lambda = PythonFunction(
            self,
            "ConnectLambda",
            handler="connect_handler",
            index="app.py",
            entry="../lambda",
        )
        disconnect_lambda = PythonFunction(
            self,
            "DisconnectLambda",
            handler="disconnect_handler",
            index="app.py",
            entry="../lambda",
        )
        message_lambda = PythonFunction(
            self,
            "MessageLambda",
            handler="message_handler",
            index="app.py",
            entry="../lambda",
        )

        ddb_table.grant_write_data(connect_lambda)
        ddb_table.grant_write_data(disconnect_lambda)
        ddb_table.grant_read_write_data(message_lambda)

        region = "ap-northeast-1"

        role = iam.Role(
            self,
            "lambda-websocket-chat-role",
            assumed_by=iam.ServicePrincipal("apigateway.amazonaws.com"),
        )
        role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                resources=[
                    connect_lambda.function_arn,
                    disconnect_lambda.function_arn,
                    message_lambda.function_arn,
                ],
                actions=["lambda:InvokeFunction"],
            )
        )

        connect_integration = apigwv2.CfnIntegration(
            self,
            "ConnectLambdaIntegration",
            api_id=api.ref,
            integration_type="AWS_PROXY",
            integration_uri=f"arn:aws:apigateway:{region}:lambda:path/2015-03-31/functions/{connect_lambda.function_arn}/invocations",
            credentials_arn=role.role_arn,
        )
        connect_route = apigwv2.CfnRoute(
            self,
            "ConnectLambdaRoute",
            api_id=api.ref,
            route_key="$connect",
            authorization_type="NONE",
            target=f"integrations/{connect_integration.ref}",
        )

        disconnect_integration = apigwv2.CfnIntegration(
            self,
            "DisconnectLambdaIntegration",
            api_id=api.ref,
            integration_type="AWS_PROXY",
            integration_uri=f"arn:aws:apigateway:{region}:lambda:path/2015-03-31/functions/{disconnect_lambda.function_arn}/invocations",
            credentials_arn=role.role_arn,
        )
        disconnect_route = apigwv2.CfnRoute(
            self,
            "DisconnectLambdaRoute",
            api_id=api.ref,
            route_key="$disconnect",
            authorization_type="NONE",
            target=f"integrations/{disconnect_integration.ref}",
        )

        message_integration = apigwv2.CfnIntegration(
            self,
            "MessageLambdaIntegration",
            api_id=api.ref,
            integration_type="AWS_PROXY",
            integration_uri=f"arn:aws:apigateway:{region}:lambda:path/2015-03-31/functions/{message_lambda.function_arn}/invocations",
            credentials_arn=role.role_arn,
        )
        message_route = apigwv2.CfnRoute(
            self,
            "MessageLambdaRoute",
            api_id=api.ref,
            route_key="sendmessage",
            authorization_type="NONE",
            target=f"integrations/{message_integration.ref}",
        )

        deployment = apigwv2.CfnDeployment(self, "lambda-websocket-chat-deployment", api_id=api.ref)

        stage = apigwv2.CfnStage(self, "lambda-websocket-chat-stage", api_id=api.ref, auto_deploy=True, deployment_id=deployment.ref, stage_name="dev")

        deps = core.ConcreteDependable()
        deps.add(connect_route)
        deps.add(disconnect_route)
        deps.add(message_route)
        deployment.node.add_dependency(deps)
        