

def get_listing_set(listings):
    new_listings = []
    # get the highest bid for each lisitng and bind them with the listing
    for i in range(len(listings)):
        listing = listings[i]
        bid_num = listing.bids.count()
        if bid_num == 0:
            highest_bid = listing.starting_bid
        else:
            highest_bid = listing.bids.order_by("-price").first().price

        new_listings.append({
            "listing": listing,
            "highest_bid": highest_bid
        })
    return new_listings