#include <iostream>
#include <vector>

using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int n, v; cin >> n >> v;
    vector<int> w(n);
    for (int &x: w) cin >> x;
    int ans = 0;
    for (int i = 0; i < n; i++) {
        for (int j = i+1; j < n; j++) {
            for (int k = j+1; k < n; k++) {
                if (i + j + k + 3 > v) continue;
                ans = max(ans, w[i] + w[j] + w[k]);
            }
        }
    }
    cout << ans << "\n";

    return 0;
}