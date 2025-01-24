module access_control::gate {
    use std::signer;
    use aptos_framework::coin;

    // Tracks whether an account has access
    struct AccessControl has key {
        use_agent: bool,
    }

    // Grants access if the user holds enough tokens of a specific type
    public entry fun set_access<UserCoin>(
        user: &signer,
        required_balance: u64
    ) acquires AccessControl {
        let user_addr = signer::address_of(user);
        let balance = coin::balance<UserCoin>(user_addr);

        // Ensure the user has enough tokens
        assert!(balance >= required_balance, 1);

        if (!exists<AccessControl>(user_addr)) {
            move_to(user, AccessControl { use_agent: true });
        } else {
            let access = borrow_global_mut<AccessControl>(user_addr);
            access.use_agent = true;
        }
    }

    // Checks if an account has access
    public fun check_access(account: address): bool acquires AccessControl {
        if (exists<AccessControl>(account)) {
            let access = borrow_global<AccessControl>(account);
            access.use_agent
        } else {
            false
        }
    }
}