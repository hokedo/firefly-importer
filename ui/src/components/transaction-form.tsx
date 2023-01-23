import {useForm} from "react-hook-form";
import {Input} from "./input";
import {Dropdown} from "./dropdown";
import {SearchInput} from "./search-input";

const RON = 'RON';
const EUR = 'EUR';
const CURRENCIES = {RON, EUR}

const WITHDRAWAL = 'Withdrawal';
const DEPOSIT = 'Deposit';
const TRANSFER = 'Transfer';
const TRANSFER_TYPES = {WITHDRAWAL, DEPOSIT, TRANSFER}

const TransactionForm = () => {
    const {register, handleSubmit} = useForm();
    const onSubmit = (data: any) => console.log(data);

    return (
        <form onSubmit={handleSubmit(onSubmit)}>
            <div>
                <Dropdown name={'transfer_type'} options={TRANSFER_TYPES} register={register}/>
            </div>

            <div>
                <Input name='description' register={register}/>
            </div>

            <div>
                <Input name='source_account' register={register}/>
                <Input name='destination_account' register={register}/>
            </div>

            <div>
                <Input name='date' type='date' register={register}/>
            </div>

            <div>
                <SearchInput name='category' dataList={['test', 'category 2']} register={register}/>
            </div>


            <div>
                <Input name='amount' type='number' register={register}/>
                <Dropdown name={'currency'} options={CURRENCIES} register={register}/>
            </div>

            <div>
                <Input name='foreign_amount' type='number' register={register}/>
                <Dropdown name={'foreign_currency'} options={CURRENCIES} register={register}/>
            </div>
            <div>
                <input type="submit"/>
            </div>
        </form>
    );

}

export default TransactionForm;
