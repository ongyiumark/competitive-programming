#include <iostream>
#include <vector>
#include <algorithm>

using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n, k; cin >> n >> k;
    vector<int> a(n), b(n);
    for (int &x : a) cin >> x;
    for (int i = 0; i < n; i++) b[i] = a[i];
    sort(b.begin(), b.end());

    int l = -1, r = -1;
    for (int i = 0; i < n; i++) {
        if (a[i] != b[i]) {
            if (l == -1) l = i;
            r = i;
        }
    }

    cout << (r-l+1 <= k ? "Yes\n" : "No\n");
    return 0;
}