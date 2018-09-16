class Object {
 public:
  int bad_access_ = 0;
 private:
  int good_access_ = 0;
  int bad_name = 0;
  int BadName_ = 0;
};

int Main() {
  return 0;
}
