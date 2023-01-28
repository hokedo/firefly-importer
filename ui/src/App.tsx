import React, {useEffect, useState} from 'react';
import useWebSocket, {ReadyState} from 'react-use-websocket';
import TransactionForm from "./components/transaction-form";
import {UploadFileInput} from "./components/upload-file-input";
import LoadingModal from "./components/loading-modal";

const WS_URL = 'ws://127.0.0.1:8000';


const WS_CONNECTION_STATUSES = {
    [ReadyState.CONNECTING]: 'Connecting',
    [ReadyState.OPEN]: 'Open',
    [ReadyState.CLOSING]: 'Closing',
    [ReadyState.CLOSED]: 'Closed',
    [ReadyState.UNINSTANTIATED]: 'Uninstantiated',
};


function App() {
    const {
        sendJsonMessage,
        lastJsonMessage,
        readyState
    } = useWebSocket<{ transactions?: any, info?: string, error?: string } | null>(WS_URL, {
        onOpen: () => {
            console.log('WebSocket connection established.');
        }
    });
    const connectionStatus = WS_CONNECTION_STATUSES[readyState];
    const wsConnectionClosed = readyState !== ReadyState.OPEN;
    const [index, setIndex] = useState(0);
    const [fileSent, setFileSent] = useState(false);
    const [transactions, setTransactions] = useState<any[] | null>(null);
    const [serverLogs, setServerLogs] = useState("");


    const receivedTransactions = transactions != null;
    const showLoadingSpinner = fileSent && !receivedTransactions;

    const onSubmit = (data: any) => {
        sendJsonMessage({transaction: data});

        if (transactions != null && index + 1 < transactions.length)
            setIndex(index + 1);
        else {
            setTransactions(null);
            setFileSent(false);
        }
    };

    const onFileUpload = (content: any) => {
        sendJsonMessage({content});
        setIndex(0);
        setFileSent(true);
    };

    useEffect(() => {
        if (lastJsonMessage?.transactions != null) {
            setTransactions(lastJsonMessage?.transactions)
        }
    }, [lastJsonMessage?.transactions])

    // Show server logs in textbox area
    useEffect(() => {
        if (lastJsonMessage?.info != null) {
            setServerLogs(lastJsonMessage.info + "\n" + serverLogs);
        }
    }, [lastJsonMessage?.info]);

    useEffect(() => {
        if (lastJsonMessage?.error != null) {
            setServerLogs(lastJsonMessage.error + "\n" + serverLogs);

            // TODO: issue when the transaction is the last once since onSubmit reset it
            setIndex(index - 1);
        }
    }, [lastJsonMessage?.error])


    return (
        <>
            <LoadingModal hidden={!showLoadingSpinner}/>
            <div className='flex h-screen'>
                <div className='m-auto'>
                    <span className={
                        `block uppercase tracking-wide text-gray-700 text-xs font-bold mb-2 ${wsConnectionClosed ? 'text-red-600' : ''}`
                    }>
                        The WebSocket is currently {connectionStatus}
                    </span>
                    <textarea readOnly
                              id="serverLogs" rows={4} value={serverLogs}
                              className="block p-2.5 mb-2 w-full text-sm text-gray-900 bg-gray-50 rounded-lg border border-gray-300 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
                    />

                    <UploadFileInput name='upload-file' onUpload={onFileUpload}
                                     disabled={wsConnectionClosed}/>
                    {
                        receivedTransactions && !wsConnectionClosed
                            ?
                            <TransactionForm onSubmit={onSubmit} defaultValues={transactions[index]}/>
                            : <TransactionForm onSubmit={onSubmit}/>
                    }
                </div>
            </div>
        </>
    );
}

export default App;
