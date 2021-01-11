import React, { useEffect, useState, useRef } from 'react';
import {usePdf} from '@mikecousins/react-pdf';

const App = () => {
  const canvasRef = useRef(null);
  const [page, setPage] = useState(1);

  const { pdfDocument, pdfPage } = usePdf({
    file: 'test.pdf',
    page,
    canvasRef,
  });

  useEffect(() => {
    if(pdfDocument){
      const socket = new WebSocket("ws://localhost:5001/")
      socket.onopen = (event) => {
        // クライアント接続時
        console.log("onopen", event);
      };
  
      socket.onmessage = (event) => {
        // サーバーからのメッセージ受信時
        console.log("onmessgae", event);
        console.log("pdfDocument", pdfDocument);
        if (event.data.startsWith("next") && page !== pdfDocument.numPages){
          setPage(page + 1);
        }
        else if (event.data.startsWith("prev") && page !== 1){
          setPage(page - 1);
        }
      };
  
      socket.onclose = (event) => {
        // クライアント切断時
        console.log("onclose", event);
      };
      return () => {
        socket.close();
      }
    }
  }, [pdfDocument, page]);

  return (
    <div>
{!pdfDocument && <span>Loading...</span>}
      <canvas ref={canvasRef} style={{border: "1px solid blue"}} />
      {Boolean(pdfDocument && pdfDocument.numPages) && (
        <nav>
          <button disabled={page === 1} onClick={() => setPage(page - 1)}>
            Previous
          </button>
          <button
            disabled={page === pdfDocument.numPages}
            onClick={() => setPage(page + 1)}
          >
            Next
          </button>
          <span>page: {page}</span>
        </nav>
      )}
    </div>
  );
};

export default App