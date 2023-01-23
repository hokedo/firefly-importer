type onUploadCallback = (content: string | ArrayBuffer | null) => any;

interface InputProps {
    name: string;
    onUpload: onUploadCallback;
    disabled?: boolean;
}


export const UploadFileInput = ({name, onUpload, disabled}: InputProps) => {
    const readFileCallback = (file: File) => {

        const fileReader = new FileReader();
        fileReader.addEventListener('loadend', () => onUpload(fileReader.result));
        fileReader.readAsText(file);
    }

    return (
        <>
            <input
                type='file'
                disabled={disabled}
                onChange={e => !!e.target.files && readFileCallback(e.target.files[0])}
                className='block appearance-none w-full bg-gray-200 border border-gray-200 text-gray-700 py-3 px-4 pr-8 rounded leading-tight focus:outline-none focus:bg-white focus:border-gray-500'
            />
        </>
    )
};