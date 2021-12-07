#[derive(thiserror::Error, Debug)]
pub enum Error {
    #[error(transparent)]
    RsWorkdaysError(#[from] rs_workdays::Error),

    #[error("key error for argment: {arg_name:?}, key:{key_name:?}")]
    ArgKeyError{arg_name: String, key_name: String},
}