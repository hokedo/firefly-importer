import React, {useState} from 'react';
import useWebSocket, {ReadyState} from 'react-use-websocket';
import TransactionForm from "./components/transaction-form";
import {UploadFileInput} from "./components/upload-file-input";

const WS_URL = 'ws://127.0.0.1:8000';

function App() {
    const [index, setIndex] = useState(0);

    const {sendJsonMessage, lastJsonMessage, readyState} = useWebSocket<{ results: any } | null>(WS_URL, {
        onOpen: () => {
            console.log('WebSocket connection established.');
        }
    });

    const onSubmit = (data: any) => {
        console.log(data)
        setIndex(index + 1);
    };

    const onFileUpload = (content: any) => {
        sendJsonMessage({content});
    };

    const connectionStatus = {
        [ReadyState.CONNECTING]: 'Connecting',
        [ReadyState.OPEN]: 'Open',
        [ReadyState.CLOSING]: 'Closing',
        [ReadyState.CLOSED]: 'Closed',
        [ReadyState.UNINSTANTIATED]: 'Uninstantiated',
    }[readyState];


    return (
        <div className='flex h-screen'>
            <div className='m-auto'>
                <span className='block uppercase tracking-wide text-gray-700 text-xs font-bold mb-2'>
                    The WebSocket is currently {connectionStatus}
                </span>
                <UploadFileInput name='upload-file' onUpload={onFileUpload} disabled={readyState !== ReadyState.OPEN}/>
                <TransactionForm onSubmit={onSubmit} defaultValues={lastJsonMessage?.results[index]}/>
            </div>
        </div>
    );
}

export default App;
