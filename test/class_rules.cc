class Object {
  int bad_access1_ = 0;
 private:
  int good_access1_ = 0;
 public:
  int bad_access2_ = 0;
 private:
  int good_access2_ = 0;
 public:
  int bad_access3_ = 0;
};
class badName {};
class Bad_Name {};

int Main() {
  return 0;
}
