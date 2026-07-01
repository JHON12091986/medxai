use soroban_sdk::{Env, Address};

/// Trait for admin management in contracts.
pub trait AdminTrait {
    /// Transfers admin rights to a new address.
    ///
    /// # Arguments
    /// * `new_admin` - The address of the new admin.
    ///
    /// # Errors
    /// * Returns `AdminError::Unauthorized` if the caller is not the current admin.
    /// * Returns `AdminError::InvalidAddress` if the new admin address is invalid.
    fn transfer_admin(env: Env, new_admin: Address) -> Result<(), AdminError>;

    /// Returns the current admin address.
    fn get_admin(env: &Env) -> Address;
}