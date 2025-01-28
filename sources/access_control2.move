module access_control::gate2 {
    use std::signer;
    use aptos_framework::coin;

    /// A brand-new resource for demonstration
    struct AccessControl2 has key {
        use_agent2: bool,
    }

    /// An entry function that sets access if you have enough coins
    public entry fun set_access2<UserCoin>(
        user: &signer,
        required_balance: u64
    ) acquires AccessControl2 {
        let user_addr = signer::address_of(user);
        let balance = coin::balance<UserCoin>(user_addr);
        assert!(balance >= required_balance, 101);

        if (!exists<AccessControl2>(user_addr)) {
            move_to(user, AccessControl2 { use_agent2: true });
        } else {
            let access2 = borrow_global_mut<AccessControl2>(user_addr);
            access2.use_agent2 = true;
        }
    }

    /// A read function that checks if an address has agent2 access
    public fun check_access2(account: address): bool acquires AccessControl2 {
        if (exists<AccessControl2>(account)) {
            let a2 = borrow_global<AccessControl2>(account);
            a2.use_agent2
        } else {
            false
        }
    }

    /// This is guaranteed to be recognized as a view function 
    /// because it doesn't read or write any global resources
    #[view]
    public fun get_meaning_of_view(): u64 {
        42
    }
}
