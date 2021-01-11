const socket = new WebSocket(
    "wss://5jay1t106f.execute-api.ap-northeast-1.amazonaws.com/undefined/"
  );

  function sendMessage() {
      socket.post
  }
  
  function WebSocketComponent() {
    React.useEffect(() => {
      socket.onopen = (event) => {
        // クライアント接続時
        console.log("onopen", event);
      };
  
      socket.onmessage = (event) => {
        // サーバーからのメッセージ受信時
        console.log("onmessgae", event);
      };
  
      socket.onclose = (event) => {
        // クライアント切断時
        console.log("onclose", event);
      };
  
      return () => {
        socket.close();
      };
    });
  
    return (
      <div>
        <p>WebSocketComponent</p>
      </div>
    );
  }
  
  export default WebSocketComponent;