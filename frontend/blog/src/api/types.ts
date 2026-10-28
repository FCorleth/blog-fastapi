export type Token = {
  access_token: string;
  refresh_token: string;
};

export type UserPrivate = {
  id: number;
  username: string;
  email: string;
  image_file: string | null;
  image_path: string;
};
