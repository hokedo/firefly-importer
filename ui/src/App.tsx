import React from 'react';
import useWebSocket from 'react-use-websocket';
import './App.css';
import TransactionForm from "./components/transaction-form";

const WS_URL = 'ws://127.0.0.1:8000';

function App() {
    useWebSocket(WS_URL, {
        onOpen: () => {
            console.log('WebSocket connection established.');
        }
    });

    return (
        <div className='flex h-screen dark:bg-slate-800'>
            <div className='m-auto bg-white'>
                <TransactionForm/>
            </div>
        </div>
    );
}

export default App;
