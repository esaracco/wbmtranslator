#!/usr/bin/perl

# Copyright (C) 2004-2019
# Emmanuel Saracco <emmanuel@esaracco.fr>
#
# GNU GENERAL PUBLIC LICENSE

require './translator-lib.pl';

my $app = $in{'app'};
my $lang = $in{'t'};
my $webmin_lang = $in{'webmin_lang'};
my $filter_modified = defined ($in{'filter_modified'});
my %file_ref = ($webmin_lang eq 'lang') ?
     &trans_get_items ("$root_directory/lang/$ref_lang") :
     &trans_get_items (&trans_get_path ($app, "lang/$ref_lang"));
my %file = ($webmin_lang eq 'lang') ?
     &trans_get_items ("$root_directory/lang/$lang") :
     &trans_get_items (&trans_get_path ($app, "lang/$lang"));
my %removed = &trans_get_hash_diff_removed ($ref_lang, $lang, \%file_ref, \%file);
my %new = &trans_get_hash_diff_new ($ref_lang, $lang, \%file_ref, \%file);
my @updated = &trans_get_array_updated ( 'interface', $ref_lang, $app);

foreach my $key (keys (%removed))
{
  $file_ref{"$key"} = $removed{"$key"};
};

foreach my $key (keys (%new))
{
  delete $file_ref{"$key"};
};

##### POST actions #####
#
# update translation file
if (defined ($in{'update'}))
{
  ($webmin_lang eq 'lang') ?
    open (H, '>', "$root_directory/lang/$lang") :
    open (H, '>', &trans_get_path ($app, "lang/$lang"));
  foreach my $item (sort keys %in)
  {
    if ($item =~ s/newitem_//)
    {
      $in{"newitem_$item"} =~ s/(\r\n|\n)/ /g;
      print H $item.'='.$in{"newitem_$item"}."\n";
    }
  }
  close (H);

  # FIXME
  # do not HTML encode webmin "/lang/*" files
  ($webmin_lang eq 'lang') ?
    &trans_char2ent ("$root_directory/lang/$lang", 'work') :
    &trans_char2ent (&trans_get_path ($app, "lang/$lang"), 'html');

  &redirect ("interface_main.cgi?app=$app&t=$lang&o=update_trans&webmin_lang=$webmin_lang");
  exit;
}
#
########################

&trans_header ($text{'EDIT_TITLE'}, $app, $lang);

print qq(<br/>);
if ($ref_lang ne $lang)
{
  printf qq($text{'EDIT_DESCRIPTION1'}), $ref_lang, $lang;
}
else
{
  printf qq($text{'EDIT_DESCRIPTION2'}), $ref_lang;
}
print qq(</p>);

print qq(<form action="interface_edit.cgi" method="post">);
print qq(<input type="hidden" name="app" value="$app">);
print qq(<input type="hidden" name="t" value="$lang">);
print qq(<input type="hidden" name="webmin_lang" value="$webmin_lang">);

print qq(<div class="btn-group"><button type="submit" class="btn btn-default btn-tiny ui_form_end_submit" name="filter_modified"><i class="fa fa-fw fa-filter"></i> <span>$text{'ONLY_MODIFIED'}</span></button>&nbsp;<button type="submit" class="btn btn-default btn-tiny ui_form_end_submit"><i class="fa fa-fw fa-filter"></i> <span>$text{'DISPLAY_ALL'}</span></button></div>);

print qq(
  <p/><div style="text-align:center">
    <span class="circle success"></span> = $text{'TRANSLATED'},
    <span class="circle warning"></span> = $text{'MODIFIED'}
  </div>
);

print qq(<p/><table class="trans keys-values" width="100%">);
foreach my $key (sort keys %file_ref)
{
  my %hash = ();
  my $panel = '';
  my $modified = 0;
  
  %hash = &trans_get_item_updated (\@updated, $key);
  $modified = ($hash{'key'} eq $key);

  # modified
  if ($modified)
  {
    $panel = qq(<tr><td><span class="circle warning"></span>&nbsp;$key:</td><td></td></tr>);
    $panel .= qq(<tr><td></td>);

    $panel .= sprintf (qq(<td>
    <table class="trans keys-values" width="100%">
    <tr>
      <td nowrap><b>$text{'OLD_STRING'}:</b></td>
      <td class="to-translate" style="background:#ffff77">%s</td>
    </tr>), &html_escape($hash{'old'}));

    if ($ref_lang ne $lang)
    {
      $panel .= sprintf (qq(
        <tr>
          <td nowrap><b>$text{'NEW_STRING'}:</b></td>
          <td class="to-translate" style="background:#aaffaa">%s</td>
       </tr>), &html_escape($hash{'new'}));
    }

    $panel .= qq(</table></td></tr>);
  }
  # translated
  else
  {
    $panel = sprintf (qq(<tr><td><span class="circle success"></span>&nbsp;$key:</td><td class="to-translate">%s</td></tr>), &html_escape($file_ref{$key}));
  };

  if ($filter_modified && !$modified) 
  {
    print qq(<input type="hidden" name="newitem_$key" value=");
    print (($in{"newitem_$key"} ne '') ? 
      &html_escape ($in{"newitem_$key"}) : &html_escape ($file{$key}));

    print qq(">);
  }
  else
  {
    print qq(
      $panel
      <tr><td></td><td>
      <textarea name="newitem_$key" rows=5>);
    print (($in{"newitem_$key"} ne '') ? 
                           $in{"newitem_$key"} : $file{$key});

    print qq(</textarea></td></tr>);
  }
}

print qq(</table>);
print qq(<p>);
print qq(<p/><div><button type="submit" name="update" class="btn btn-success ui_form_end_submit"><i class="fa fa-fw fa-check-circle-o"></i> <span>$text{'UPDATE_TRANSLATION_FILE'}</span></button></div>);
print qq(</p>);
print qq(</form>);

&trans_footer ("interface_main.cgi?app=$app&webmin_lang=$webmin_lang", $text{'INTERFACE_INDEX'});
